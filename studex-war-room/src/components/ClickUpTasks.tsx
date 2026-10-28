/**
 * ClickUpTasks — War Room TASKS Tab
 * Displays Coffee / Caviar / Biltong tasks in ops command-center style
 *
 * Uses taste-skill design principles:
 * DENSITY 8 — high information density, compact rows
 * VARIANCE 6 — asymmetric split layout, color-coded by product
 */

import { useState, useEffect, useCallback } from 'react';
import { ClickUpTask, getAllTasks, PRIORITY_CONFIG, getStatusColor, formatDueDate, LISTS } from '../services/clickup';

// ClickUp is read through a server-side route. The API token must never be a
// browser variable: Vite inlines every VITE_-prefixed variable into the bundle,
// which would publish the token to every visitor.
const CLICKUP_PROXY = import.meta.env.VITE_CLICKUP_PROXY_URL as string | undefined;

const PRODUCT_COLORS: Record<string, string> = {
  coffee:  '#d4a017',
  caviar:  '#3b82f6',
  biltong: '#22c55e',
};
const PRODUCT_ICONS: Record<string, string> = {
  coffee:  '☕',
  caviar:  '🐟',
  biltong: '🥩',
};

type Filter = 'all' | 'coffee' | 'caviar' | 'biltong';
type SortBy = 'priority' | 'due' | 'status' | 'name';

export default function ClickUpTasks() {
  const [tasks, setTasks] = useState<Record<string, ClickUpTask[]>>({ coffee: [], caviar: [], biltong: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>('all');
  const [sortBy, setSortBy] = useState<SortBy>('status');
  const [lastSync, setLastSync] = useState<Date | null>(null);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAllTasks();
      setTasks(data);
      setLastSync(new Date());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchTasks, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  // Sort comparator
  const sortTasks = (arr: ClickUpTask[]): ClickUpTask[] => {
    return [...arr].sort((a, b) => {
      if (sortBy === 'priority') {
        const order = ['urgent', 'high', 'medium', 'low', 'null'];
        const ai = order.indexOf(String(a.priority).toLowerCase());
        const bi = order.indexOf(String(b.priority).toLowerCase());
        return ai - bi;
      }
      if (sortBy === 'due') {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return parseInt(a.due_date) - parseInt(b.due_date);
      }
      if (sortBy === 'status') return a.status.status.localeCompare(b.status.status);
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      return 0;
    });
  };

  const allTasks = filter === 'all'
    ? [...tasks.coffee, ...tasks.caviar, ...tasks.biltong]
    : tasks[filter] || [];

  const sorted = sortTasks(allTasks);

  const countByProduct = (product: string) => (tasks[product] || []).length;
  const totalCount = sorted.length;

  if (!CLICKUP_PROXY) {
    return (
      <div className="clickup-tasks">
        <div className="cu-setup">
          <div className="cu-setup-icon">🔗</div>
          <div className="cu-setup-title">CLICKUP SERVER PROXY NOT CONFIGURED</div>
          <div className="cu-setup-desc">
            ClickUp is read through a server-side route. The API token must never sit in
            a browser variable &mdash; Vite inlines every VITE_-prefixed variable into the
            bundle, which publishes the token to every visitor.
          </div>
          <div className="cu-setup-code">
{`VITE_CLICKUP_PROXY_URL=/api/clickup
VITE_CLICKUP_LIST_COFFEE=your_coffee_list_id
VITE_CLICKUP_LIST_CAVIAR=your_caviar_list_id
VITE_CLICKUP_LIST_BILTONG=your_biltong_list_id`}
          </div>
          <div className="cu-setup-steps">
            <div className="cu-step">
              <span className="cu-step-n">1</span>
              <span>Point VITE_CLICKUP_PROXY_URL at a server route that holds the token</span>
            </div>
            <div className="cu-step">
              <span className="cu-step-n">2</span>
              <span>That route calls api.clickup.com and adds the Authorization header server-side</span>
            </div>
            <div className="cu-step">
              <span className="cu-step-n">3</span>
              <span>Open each List → copy URL → extract List ID from v/l/ID</span>
            </div>
            <div className="cu-step">
              <span className="cu-step-n">4</span>
              <span>Set the proxy URL + list IDs in the War Room .env, restart dev server</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="clickup-tasks">
      {/* Header */}
      <div className="cu-header">
        <div className="cu-title-row">
          <span className="cu-icon">📋</span>
          <span className="cu-title">CLICKUP TASKS</span>
          <span className="cu-count">{totalCount} tasks</span>
          {lastSync && (
            <span className="cu-sync">
              SYNCED {lastSync.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>

        {/* Product filter tabs */}
        <div className="cu-filters">
          {(['all', 'coffee', 'caviar', 'biltong'] as Filter[]).map(f => (
            <button
              key={f}
              className={`cu-filter-btn ${filter === f ? 'active' : ''}`}
              style={filter === f && f !== 'all' ? { borderColor: PRODUCT_COLORS[f], color: PRODUCT_COLORS[f] } : {}}
              onClick={() => setFilter(f)}
            >
              {f !== 'all' && <span>{PRODUCT_ICONS[f]}</span>}
              {f.toUpperCase()}
              <span className="cu-filter-count">
                {f === 'all' ? totalCount : countByProduct(f)}
              </span>
            </button>
          ))}

          <div className="cu-sort-row">
            <span className="cu-sort-label">SORT:</span>
            {(['status', 'priority', 'due', 'name'] as SortBy[]).map(s => (
              <button
                key={s}
                className={`cu-sort-btn ${sortBy === s ? 'active' : ''}`}
                onClick={() => setSortBy(s)}
              >
                {s.toUpperCase()}
              </button>
            ))}
          </div>

          <button className="cu-refresh-btn" onClick={fetchTasks} disabled={loading}>
            {loading ? '↻ LOADING…' : '↻ REFRESH'}
          </button>
        </div>
      </div>

      {error && (
        <div className="cu-error">
          <span className="cu-error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Task table */}
      {!loading && !error && (
        <div className="cu-table-wrap">
          <table className="cu-table">
            <thead>
              <tr>
                <th>PRODUCT</th>
                <th>TASK NAME</th>
                <th>STATUS</th>
                <th>PRIORITY</th>
                <th>DUE</th>
                <th>ASSIGNEE</th>
              </tr>
            </thead>
            <tbody>
              {sorted.length === 0 && (
                <tr>
                  <td colSpan={6} className="cu-empty">
                    NO TASKS — all clear or wrong list IDs
                  </td>
                </tr>
              )}
              {sorted.map((task: ClickUpTask) => {
                const product = task.list_id === LISTS.COFFEE ? 'coffee'
                  : task.list_id === LISTS.CAVIAR ? 'caviar' : 'biltong';
                const priority = PRIORITY_CONFIG[String(task.priority).toLowerCase()] || PRIORITY_CONFIG['null'];
                const statusColor = getStatusColor(task.status?.status || '');
                const isOverdue = task.due_date && parseInt(task.due_date) < Date.now();

                return (
                  <tr
                    key={task.id}
                    className={`cu-task-row ${isOverdue ? 'overdue' : ''}`}
                    onClick={() => window.open(task.url, '_blank')}
                  >
                    <td>
                      <div className="cu-product-badge" style={{ borderColor: PRODUCT_COLORS[product], color: PRODUCT_COLORS[product] }}>
                        {PRODUCT_ICONS[product]} {product.toUpperCase()}
                      </div>
                    </td>
                    <td>
                      <div className="cu-task-name">{task.name}</div>
                      <div className="cu-task-id">{task.custom_id || task.id}</div>
                    </td>
                    <td>
                      <div className="cu-status-badge" style={{ color: statusColor, borderColor: statusColor }}>
                        {task.status?.status || '—'}
                      </div>
                    </td>
                    <td>
                      <div className="cu-priority" style={{ color: priority.color }}>
                        {priority.emoji} {priority.label}
                      </div>
                    </td>
                    <td>
                      <div className={`cu-due ${isOverdue ? 'overdue' : ''}`}>
                        {isOverdue ? '⚠️ ' : ''}{formatDueDate(task.due_date)}
                      </div>
                    </td>
                    <td>
                      {task.assignee ? (
                        <div className="cu-assignee">
                          {task.assignee.profilePicture ? (
                            <img
                              src={task.assignee.profilePicture}
                              alt={task.assignee.username}
                              className="cu-avatar"
                            />
                          ) : (
                            <div className="cu-avatar-placeholder">
                              {task.assignee.username[0].toUpperCase()}
                            </div>
                          )}
                          <span>{task.assignee.username}</span>
                        </div>
                      ) : (
                        <span className="cu-unassigned">UNASSIGNED</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
