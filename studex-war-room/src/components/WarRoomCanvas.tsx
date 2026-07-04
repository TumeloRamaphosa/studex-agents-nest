import { useEffect, useRef, useState, useMemo } from 'react';
import * as THREE from 'three';
import { GraphNode, GraphEdge, buildGraphData } from '../data/graphData';

interface Props {
  onNodeSelect: (node: GraphNode | null) => void;
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  onNodeHover: (id: string | null) => void;
}

interface SimulatedNode extends GraphNode {
  vx: number; vy: number; vz: number;
  fx: number; fy: number; fz: number;
}

function hexToRgb(hex: string): THREE.Color {
  return new THREE.Color(hex);
}

export default function WarRoomCanvas({ onNodeSelect, selectedNodeId, hoveredNodeId, onNodeHover }: Props) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    particles: THREE.Points;
    lines: THREE.LineSegments;
    spheres: THREE.Mesh[];
    glows: THREE.Mesh[];
    nodeMap: Map<THREE.Mesh, GraphNode>;
    glowMap: THREE.Mesh | null;
    lineSegments: { positions: Float32Array; colors: Float32Array; count: number };
    raycaster: THREE.Raycaster;
    mouse: THREE.Vector2;
    isDragging: boolean;
    prevMouse: { x: number; y: number };
    rotationVelocity: { x: number; y: number };
    animId: number;
    group: THREE.Group;
  } | null>(null);
  const [initialized, setInitialized] = useState(false);

  // Initialize Three.js scene
  useEffect(() => {
    if (!mountRef.current) return;
    const container = mountRef.current;

    const { nodes: rawNodes, edges, nodeMap } = buildGraphData();

    // Simulate forces to get node positions
    const simNodes: SimulatedNode[] = rawNodes.map((n, i) => {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 6 + Math.random() * 4;
      return {
        ...n,
        x: r * Math.sin(phi) * Math.cos(theta),
        y: r * Math.sin(phi) * Math.sin(theta),
        z: r * Math.cos(phi),
        vx: 0, vy: 0, vz: 0,
        fx: 0, fy: 0, fz: 0,
      };
    });

    // Run force simulation
    const nodePosMap = new Map<string, SimulatedNode>();
    simNodes.forEach(n => nodePosMap.set(n.id, n));

    for (let iter = 0; iter < 300; iter++) {
      simNodes.forEach(n => { n.fx = 0; n.fy = 0; n.fz = 0; });

      // Repulsion
      for (let a = 0; a < simNodes.length; a++) {
        for (let b = a + 1; b < simNodes.length; b++) {
          const na = simNodes[a], nb = simNodes[b];
          const dx = nb.x - na.x, dy = nb.y - na.y, dz = nb.z - na.z;
          const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) || 0.01;
          const repel = 12 / (dist * dist);
          const fx = (dx/dist) * repel, fy = (dy/dist) * repel, fz = (dz/dist) * repel;
          na.fx -= fx; na.fy -= fy; na.fz -= fz;
          nb.fx += fx; nb.fy += fy; nb.fz += fz;
        }
      }

      // Attraction
      edges.forEach(e => {
        const src = nodePosMap.get(e.source), tgt = nodePosMap.get(e.target);
        if (!src || !tgt) return;
        const dx = tgt.x - src.x, dy = tgt.y - src.y, dz = tgt.z - src.x;
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) || 0.01;
        const attract = 0.015;
        src.fx += dx * attract; src.fy += dy * attract; src.fz += dz * attract;
        tgt.fx -= dx * attract; tgt.fy -= dy * attract; tgt.fz -= dz * attract;
      });

      // Center gravity + apply
      simNodes.forEach(n => {
        n.fx -= n.x * 0.008; n.fy -= n.y * 0.008; n.fz -= n.z * 0.008;
        n.vx = (n.vx + n.fx * 0.5) * 0.85;
        n.vy = (n.vy + n.fy * 0.5) * 0.85;
        n.vz = (n.vz + n.fz * 0.5) * 0.85;
        n.x += n.vx; n.y += n.vy; n.z += n.vz;
      });
    }

    // Three.js setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#010810');
    scene.fog = new THREE.FogExp2('#021a28', 0.025);

    const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 2, 28);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Ambient + directional lights
    const ambientLight = new THREE.AmbientLight(0x021a2e, 2.0);
    scene.add(ambientLight);

    // Bioluminescent green primary light
    const pointLight = new THREE.PointLight(0x00ff88, 3.5, 80);
    pointLight.position.set(0, 0, 0);
    scene.add(pointLight);

    // Deep blue secondary fill
    const pointLight2 = new THREE.PointLight(0x0044ff, 1.2, 60);
    pointLight2.position.set(-10, 5, 10);
    scene.add(pointLight2);

    const group = new THREE.Group();
    scene.add(group);

    // Background star field
    // Underwater particle field — bioluminescent plankton/bubbles
    const starGeo = new THREE.BufferGeometry();
    const starCount = 4000;
    const starPositions = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starPositions[i * 3] = (Math.random() - 0.5) * 200;
      starPositions[i * 3 + 1] = (Math.random() - 0.5) * 200;
      starPositions[i * 3 + 2] = (Math.random() - 0.5) * 200;
      // Mix of toxic green and deep cyan bioluminescent
      const isGreen = Math.random() > 0.4;
      starColors[i * 3] = isGreen ? 0.0 : 0.0;
      starColors[i * 3 + 1] = isGreen ? 1.0 : 0.6;
      starColors[i * 3 + 2] = isGreen ? 0.5 : 1.0;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));
    const starMat = new THREE.PointsMaterial({
      color: 0x00ff88,
      size: 0.22,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.6,
      vertexColors: true,
    });
    const stars = new THREE.Points(starGeo, starMat);
    group.add(stars);

    // Node meshes
    const spheres: THREE.Mesh[] = [];
    const glows: THREE.Mesh[] = [];
    const meshNodeMap = new Map<THREE.Mesh, GraphNode>();


    simNodes.forEach(node => {
      const color = hexToRgb(node.color);

      // Glow sphere
      const glowGeo = new THREE.SphereGeometry(node.size * 0.55, 16, 16);
      const glowMat = new THREE.MeshBasicMaterial({
        color: hexToRgb(node.glowColor),
        transparent: true,
        opacity: 0.08,
        side: THREE.BackSide,
      });
      const glow = new THREE.Mesh(glowGeo, glowMat);
      glow.position.set(node.x, node.y, node.z);
      group.add(glow);
      glows.push(glow);

      // Main sphere
      const geo = new THREE.SphereGeometry(node.size * 0.38, 24, 24);
      const mat = new THREE.MeshStandardMaterial({
        color,
        emissive: hexToRgb(node.glowColor),
        emissiveIntensity: 0.6,
        metalness: 0.7,
        roughness: 0.2,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(node.x, node.y, node.z);
      mesh.userData = node;
      group.add(mesh);
      spheres.push(mesh);
      meshNodeMap.set(mesh, node);
    });

    // Line segments for edges
    const edgePositions: number[] = [];
    const edgeColors: number[] = [];
    edges.forEach(e => {
      const src = nodePosMap.get(e.source);
      const tgt = nodePosMap.get(e.target);
      if (!src || !tgt) return;
      const color = hexToRgb(e.color === '#ff8800' ? '#ff8800' : e.color === '#d4a017' ? '#d4a017' : e.color);

      edgePositions.push(src.x, src.y, src.z, tgt.x, tgt.y, tgt.z);
      for (let i = 0; i < 2; i++) {
        edgeColors.push(color.r, color.g, color.b);
      }
    });

    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(edgePositions), 3));
    lineGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(edgeColors), 3));
    const lineMat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.4 });
    const lineSegments = new THREE.LineSegments(lineGeo, lineMat);
    group.add(lineSegments);

    // Particle system along edges (ambient connection dots)
    const particlePositions: number[] = [];
    const particleColors: number[] = [];
    const particleCount = 600;
    for (let i = 0; i < particleCount; i++) {
      const edge = edges[i % edges.length];
      const src = nodePosMap.get(edge.source);
      const tgt = nodePosMap.get(edge.target);
      if (!src || !tgt) continue;
      const t = Math.random();
      particlePositions.push(
        src.x + (tgt.x - src.x) * t,
        src.y + (tgt.y - src.y) * t,
        src.z + (tgt.z - src.z) * t,
      );
      const c = hexToRgb(edge.color === '#ff8800' ? '#ff8800' : edge.color === '#d4a017' ? '#d4a017' : edge.color);
      particleColors.push(c.r, c.g, c.b);
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(particlePositions), 3));
    pGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(particleColors), 3));
    const pMat = new THREE.PointsMaterial({ size: 0.22, vertexColors: true, transparent: true, opacity: 0.85 });
    const particles = new THREE.Points(pGeo, pMat);
    group.add(particles);

    const raycaster = new THREE.Raycaster();
    raycaster.params.Points = { threshold: 0.3 };
    const mouse = new THREE.Vector2();

    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    const rotationVelocity = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
      rotationVelocity.x = 0; rotationVelocity.y = 0;
    };

    const onMouseMove = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (isDragging) {
        const dx = e.clientX - prevMouse.x;
        const dy = e.clientY - prevMouse.y;
        rotationVelocity.y = dx * 0.004;
        rotationVelocity.x = dy * 0.004;
        prevMouse = { x: e.clientX, y: e.clientY };
      }
    };

    const onMouseUp = () => { isDragging = false; };

    const onClick = (e: MouseEvent) => {
      if (Math.abs(rotationVelocity.x) > 0.01 || Math.abs(rotationVelocity.y) > 0.01) return;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(spheres);
      if (intersects.length > 0) {
        const node = meshNodeMap.get(intersects[0].object as THREE.Mesh);
        onNodeSelect(node || null);
      } else {
        onNodeSelect(null);
      }
    };

    const onResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };

    renderer.domElement.addEventListener('mousedown', onMouseDown);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('mouseup', onMouseUp);
    renderer.domElement.addEventListener('click', onClick);
    window.addEventListener('resize', onResize);

    // Store refs
    const ref = {
      scene, camera, renderer, particles, lines: lineSegments,
      spheres, glows, nodeMap: meshNodeMap, glowMap: null as unknown as THREE.Mesh,
      lineSegments: { positions: new Float32Array(edgePositions), colors: new Float32Array(edgeColors), count: edges.length },
      raycaster, mouse, isDragging, prevMouse, rotationVelocity, animId: 0, group,
    };
    sceneRef.current = ref;

    // Animation loop
    let t = 0;
    const animate = () => {
      ref.animId = requestAnimationFrame(animate);
      t += 0.008;

      if (!isDragging) {
        group.rotation.y += 0.002 + rotationVelocity.y;
        group.rotation.x += rotationVelocity.x;
        rotationVelocity.x *= 0.95;
        rotationVelocity.y *= 0.95;
      }

      // Pulsing glows
      glows.forEach((glow, i) => {
        const scale = 1 + Math.sin(t + i * 0.5) * 0.15;
        glow.scale.setScalar(scale);
      });

      // Floating node animation
      spheres.forEach((mesh, i) => {
        const node = meshNodeMap.get(mesh);
        if (node) {
          mesh.position.y += Math.sin(t * 0.5 + i * 0.3) * 0.002;
        }
      });

      // Animate particles along edges
      const posAttr = particles.geometry.attributes.position as THREE.BufferAttribute;
      const positions = posAttr.array as Float32Array;
      const nodeList = simNodes;
      const edgeList = edges;
      for (let i = 0; i < particleCount; i++) {
        const edge = edgeList[i % edgeList.length];
        const src = nodeList.find(n => n.id === edge.source);
        const tgt = nodeList.find(n => n.id === edge.target);
        if (!src || !tgt) continue;
        const phase = (t * 0.4 + i * 0.07) % 1;
        positions[i * 3] = src.x + (tgt.x - src.x) * phase;
        positions[i * 3 + 1] = src.y + (tgt.y - src.y) * phase;
        positions[i * 3 + 2] = src.z + (tgt.z - src.z) * phase;
      }
      posAttr.needsUpdate = true;

      renderer.render(scene, camera);
    };
    animate();
    setInitialized(true);

    return () => {
      cancelAnimationFrame(ref.animId);
      renderer.domElement.removeEventListener('mousedown', onMouseDown);
      renderer.domElement.removeEventListener('mousemove', onMouseMove);
      renderer.domElement.removeEventListener('mouseup', onMouseUp);
      renderer.domElement.removeEventListener('click', onClick);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  // Update node highlight when selection changes
  useEffect(() => {
    const ref = sceneRef.current;
    if (!ref) return;
    ref.spheres.forEach(mesh => {
      const node = ref.nodeMap.get(mesh);
      const mat = mesh.material as THREE.MeshStandardMaterial;
      if (!node) return;
      if (selectedNodeId === node.id) {
        mat.emissiveIntensity = 1.2;
        mat.emissive = new THREE.Color('#ffffff');
      } else if (hoveredNodeId === node.id) {
        mat.emissiveIntensity = 1.0;
        mat.emissive = new THREE.Color(node.glowColor);
      } else {
        mat.emissiveIntensity = 0.6;
        mat.emissive = new THREE.Color(node.glowColor);
      }
    });
    // Update line opacity
    const lineMat = ref.lines.material as THREE.LineBasicMaterial;
    lineMat.opacity = selectedNodeId ? 0.6 : 0.4;
  }, [selectedNodeId, hoveredNodeId]);

  return (
    <div className="war-room-canvas" ref={mountRef}>
      {!initialized && (
        <div className="canvas-loading">
          <div className="loading-ring" />
          <span>INITIALIZING WAR ROOM...</span>
        </div>
      )}
    </div>
  );
}
