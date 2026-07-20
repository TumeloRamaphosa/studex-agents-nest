import { useState, useEffect } from 'react';
import type { Card, MemoryEntry } from './types';
import { DEFAULT_CARDS } from './types';

const STORAGE_KEY = 'studex-delivery-kanban-cards';

function loadCards(): Card[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed: Card[] = JSON.parse(stored);
      // Backfill memoryLog if missing
      return parsed.map(c => ({
        ...c,
        memoryLog: c.memoryLog ?? [],
        lastUpdatedAt: c.lastUpdatedAt ?? c.createdAt,
      }));
    }
  } catch {
    // ignore parse errors
  }
  return DEFAULT_CARDS;
}

export function makeMemoryEntry(
  actor: string,
  action: string,
): MemoryEntry {
  return {
    id: `log-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    timestamp: new Date().toISOString(),
    actor,
    action,
  };
}

export function useBoardStore() {
  const [cards, setCards] = useState<Card[]>(() => loadCards());
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cards));
    }
  }, [cards, isLoaded]);

  function getCardsByColumn(columnId: string): Card[] {
    return cards.filter(c => c.columnId === columnId);
  }

  function addCard(data: Omit<Card, 'id' | 'createdAt'> & { columnId: string }) {
    const now = new Date().toISOString();
    const newCard: Card = {
      ...data,
      id: `card-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      createdAt: now,
      memoryLog: data.memoryLog ?? [],
      lastUpdatedAt: now,
    };
    setCards(prev => [...prev, newCard]);
    return newCard;
  }

  function updateCard(id: string, updates: Partial<Omit<Card, 'id' | 'createdAt'>>) {
    setCards(prev => prev.map(c => {
      if (c.id !== id) return c;
      const updated = { ...c, ...updates, lastUpdatedAt: new Date().toISOString() };
      // Append memory log entry if lastUpdatedBy is provided
      if (updates.lastUpdatedBy) {
        updated.memoryLog = [
          makeMemoryEntry(updates.lastUpdatedBy, buildActionFromUpdates(updates)),
          ...(updated.memoryLog ?? []),
        ];
      }
      return updated;
    }));
  }

  function addMemoryEntry(cardId: string, actor: string, action: string) {
    setCards(prev => prev.map(c => {
      if (c.id !== cardId) return c;
      return {
        ...c,
        memoryLog: [makeMemoryEntry(actor, action), ...(c.memoryLog ?? [])],
        lastUpdatedAt: new Date().toISOString(),
      };
    }));
  }

  function deleteCard(id: string) {
    setCards(prev => prev.filter(c => c.id !== id));
  }

  function moveCard(cardId: string, toColumnId: string) {
    setCards(prev => prev.map(c => {
      if (c.id !== cardId) return c;
      const now = new Date().toISOString();
      const entry = makeMemoryEntry(
        c.lastUpdatedBy ?? '🤖 Charlie',
        `Card moved to ${toColumnId.replace(/-/g, ' ')}.`,
      );
      return {
        ...c,
        columnId: toColumnId,
        lastUpdatedAt: now,
        memoryLog: [entry, ...(c.memoryLog ?? [])],
      };
    }));
  }

  function moveAllCards(_cardsToMove: Card[], _toColumnId: string) {
    // preserved for API compat
  }

  return { cards, isLoaded, getCardsByColumn, addCard, updateCard, deleteCard, moveCard, moveAllCards, addMemoryEntry };
}

// ─── Helper ───────────────────────────────────────────────────────────────────

function buildActionFromUpdates(updates: Partial<Omit<Card, 'id' | 'createdAt'>>): string {
  if (updates.title) return `Updated title to "${updates.title}".`;
  if (updates.columnId) return `Moved card to ${updates.columnId.replace(/-/g, ' ')}.`;
  if (updates.deliveryCompany) return `Assigned delivery company: ${updates.deliveryCompany}.`;
  if (updates.eta) return `Updated ETA.`;
  if (updates.driverName) return `Updated driver to ${updates.driverName}.`;
  return 'Card updated.';
}
