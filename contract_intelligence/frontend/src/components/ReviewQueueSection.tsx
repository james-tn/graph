import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ContractSearchHit,
  decideReviewItem,
  getReviewStats,
  listReviewItems,
  ReviewItem,
  ReviewListResponse,
  ReviewStatsResponse,
  searchContracts,
} from '../api';
import { CheckCircle2, XCircle, RefreshCcw, AlertTriangle, Clock, ChevronLeft, ChevronRight, Search } from 'lucide-react';

const STATUS_OPTIONS = ['pending', 'confirmed', 'rejected', 'relinked', 'all'] as const;
type StatusFilter = (typeof STATUS_OPTIONS)[number];

const PAGE_SIZE = 10;

function formatDate(s?: string | null): string {
  if (!s) return '—';
  return s.length > 10 ? s.substring(0, 10) : s;
}

function confidenceBucket(conf?: number | null): { label: string; color: string } {
  if (conf == null) return { label: 'unknown', color: 'text-slate-400' };
  if (conf >= 0.85) return { label: `${(conf * 100).toFixed(1)}% (auto)`, color: 'text-emerald-300' };
  if (conf >= 0.75) return { label: `${(conf * 100).toFixed(1)}% (high)`, color: 'text-emerald-400' };
  if (conf >= 0.65) return { label: `${(conf * 100).toFixed(1)}% (medium)`, color: 'text-amber-300' };
  return { label: `${(conf * 100).toFixed(1)}% (low)`, color: 'text-rose-300' };
}

interface ReviewItemCardProps {
  item: ReviewItem;
  onDecide: (id: number, action: 'confirm' | 'reject' | 'relink', extra?: any) => Promise<void>;
  busy: boolean;
}

function ReviewItemCard({ item, onDecide, busy }: ReviewItemCardProps) {
  const [notes, setNotes] = useState('');
  const [relinkQuery, setRelinkQuery] = useState('');
  const [relinkPick, setRelinkPick] = useState<ContractSearchHit | null>(null);
  const [relinkResults, setRelinkResults] = useState<ContractSearchHit[]>([]);
  const [relinkLoading, setRelinkLoading] = useState(false);
  const [relinkError, setRelinkError] = useState<string | null>(null);
  const [showRelink, setShowRelink] = useState(false);
  const debounceRef = useRef<number | null>(null);
  const conf = confidenceBucket(item.confidence_score);
  const isPending = item.status === 'pending';

  // Debounced search whenever the query changes.
  useEffect(() => {
    if (!showRelink) return;
    const trimmed = relinkQuery.trim();
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }
    if (trimmed.length < 2) {
      setRelinkResults([]);
      setRelinkLoading(false);
      return;
    }
    setRelinkLoading(true);
    setRelinkError(null);
    debounceRef.current = window.setTimeout(async () => {
      try {
        const resp = await searchContracts({ q: trimmed, limit: 10 });
        setRelinkResults(resp.items);
      } catch (e: any) {
        setRelinkError(e?.response?.data?.detail || e?.message || 'Search failed');
        setRelinkResults([]);
      } finally {
        setRelinkLoading(false);
      }
    }, 250);
    return () => {
      if (debounceRef.current) {
        window.clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
    };
  }, [relinkQuery, showRelink]);

  const handleConfirm = async () => {
    await onDecide(item.id, 'confirm', { notes: notes || undefined });
  };
  const handleReject = async () => {
    await onDecide(item.id, 'reject', { notes: notes || undefined });
  };
  const handleRelink = async () => {
    if (!relinkPick) return;
    await onDecide(item.id, 'relink', {
      new_parent_contract_id: relinkPick.id,
      notes: notes || undefined,
    });
    // reset picker
    setRelinkPick(null);
    setRelinkQuery('');
    setRelinkResults([]);
    setShowRelink(false);
  };

  return (
    <div className="glass-dark rounded-2xl p-6 border border-slate-700/50 hover:border-purple-500/50 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase tracking-wide text-slate-400">Review #{item.id}</span>
            <span className={`text-xs uppercase px-2 py-0.5 rounded ${
              item.status === 'pending' ? 'bg-amber-500/20 text-amber-300'
                : item.status === 'confirmed' ? 'bg-emerald-500/20 text-emerald-300'
                : item.status === 'rejected' ? 'bg-rose-500/20 text-rose-300'
                : 'bg-blue-500/20 text-blue-300'
            }`}>{item.status}</span>
            <span className="text-xs text-slate-500">{formatDate(item.created_at)}</span>
          </div>
          <h3 className="text-lg font-semibold text-white">
            {item.relationship_type ?? 'related'} link
          </h3>
        </div>
        <div className={`text-2xl font-bold ${conf.color}`}>{conf.label}</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Child */}
        <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-700/40">
          <div className="text-xs uppercase tracking-wide text-blue-300 mb-2">Child contract</div>
          <div className="font-semibold text-white truncate">{item.child.title ?? '—'}</div>
          <div className="text-sm text-slate-400">
            {item.child.contract_type} • {item.child.reference_number ?? item.child.contract_identifier} • {formatDate(item.child.effective_date)}
          </div>
        </div>
        {/* Candidate parent */}
        <div className="bg-slate-900/40 p-4 rounded-xl border border-purple-700/40">
          <div className="text-xs uppercase tracking-wide text-purple-300 mb-2">Candidate parent</div>
          {item.candidate_parent ? (
            <>
              <div className="font-semibold text-white truncate">{item.candidate_parent.title ?? '—'}</div>
              <div className="text-sm text-slate-400">
                {item.candidate_parent.contract_type} • {item.candidate_parent.reference_number ?? item.candidate_parent.contract_identifier} • {formatDate(item.candidate_parent.effective_date)}
              </div>
            </>
          ) : (
            <div className="text-sm text-slate-500 italic">No candidate</div>
          )}
        </div>
      </div>

      {item.extracted_parent_reference && (
        <div className="text-sm text-slate-400 mb-3">
          <span className="text-slate-500">Extracted reference:</span>{' '}
          <code className="text-amber-300">{item.extracted_parent_reference}</code>
        </div>
      )}

      {item.top_features.length > 0 && (
        <div className="mb-4">
          <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">Top contributing features</div>
          <div className="flex flex-wrap gap-2">
            {item.top_features.slice(0, 5).map((f) => (
              <span key={f.feature} className="text-xs bg-slate-800/60 px-2 py-1 rounded text-slate-300">
                {f.feature} <span className="text-purple-300">({f.contribution.toFixed(2)})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {isPending && (
        <div className="space-y-3">
          <textarea
            placeholder="Optional review notes…"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full bg-slate-900/60 border border-slate-700 rounded-lg p-2 text-sm text-white placeholder-slate-500"
            rows={2}
          />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleConfirm}
              disabled={busy || !item.candidate_parent}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" /> Confirm link
            </button>
            <button
              onClick={handleReject}
              disabled={busy}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" /> Reject
            </button>
            <button
              onClick={() => setShowRelink((v) => !v)}
              disabled={busy}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold disabled:opacity-50"
            >
              <RefreshCcw className="w-4 h-4" /> Relink to other parent
            </button>
          </div>

          {showRelink && (
            <div className="mt-3 space-y-2 bg-slate-900/50 border border-slate-700/60 rounded-xl p-3">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by reference, identifier, or title…"
                  value={relinkQuery}
                  onChange={(e) => { setRelinkQuery(e.target.value); setRelinkPick(null); }}
                  className="flex-1 bg-slate-900/60 border border-slate-700 rounded-lg p-2 text-sm text-white placeholder-slate-500"
                  autoFocus
                />
              </div>

              {relinkError && (
                <div className="text-xs text-rose-300">{relinkError}</div>
              )}

              {relinkLoading && (
                <div className="text-xs text-slate-400 flex items-center gap-2">
                  <Clock className="w-3 h-3 animate-spin" /> Searching…
                </div>
              )}

              {!relinkLoading && relinkQuery.trim().length >= 2 && relinkResults.length === 0 && !relinkError && (
                <div className="text-xs text-slate-500 italic">No contracts match.</div>
              )}

              {relinkResults.length > 0 && (
                <ul className="max-h-56 overflow-y-auto divide-y divide-slate-800">
                  {relinkResults.map((hit) => {
                    const picked = relinkPick?.id === hit.id;
                    return (
                      <li key={hit.id}>
                        <button
                          type="button"
                          onClick={() => setRelinkPick(hit)}
                          className={`w-full text-left p-2 rounded-md text-sm transition ${
                            picked
                              ? 'bg-blue-600/30 border border-blue-400/60'
                              : 'hover:bg-slate-800/60 border border-transparent'
                          }`}
                        >
                          <div className="font-semibold text-white truncate">
                            {hit.title ?? '—'}
                          </div>
                          <div className="text-xs text-slate-400 truncate">
                            #{hit.id} • {hit.contract_type ?? '—'} • {hit.reference_number ?? hit.contract_identifier ?? '—'} • {formatDate(hit.effective_date)}
                          </div>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}

              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => { setShowRelink(false); setRelinkPick(null); setRelinkQuery(''); }}
                  className="px-3 py-1 rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleRelink}
                  disabled={busy || !relinkPick}
                  className="px-3 py-1 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {relinkPick ? `Relink to "${relinkPick.title?.slice(0, 30) ?? '#' + relinkPick.id}"` : 'Pick a parent'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {!isPending && item.reviewed_by && (
        <div className="text-xs text-slate-500">
          Reviewed by {item.reviewed_by} at {formatDate(item.reviewed_at)}
          {item.review_notes ? ` — “${item.review_notes}”` : ''}
        </div>
      )}
    </div>
  );
}

export function ReviewQueueSection() {
  const [stats, setStats] = useState<ReviewStatsResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('pending');
  const [page, setPage] = useState(0);
  const [data, setData] = useState<ReviewListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalPages = useMemo(() => {
    if (!data) return 0;
    return Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  }, [data]);

  const reload = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, list] = await Promise.all([
        getReviewStats(),
        listReviewItems({ status: statusFilter, limit: PAGE_SIZE, offset: page * PAGE_SIZE }),
      ]);
      setStats(s);
      setData(list);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, page]);

  const handleDecide = async (
    id: number,
    action: 'confirm' | 'reject' | 'relink',
    extra: any = {},
  ) => {
    setBusy(true);
    try {
      await decideReviewItem(id, { action, ...extra });
      await reload();
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Decision failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {(['pending', 'confirmed', 'rejected', 'relinked', 'total'] as const).map((k) => (
          <div key={k} className="glass-dark p-4 rounded-xl text-center">
            <div className="text-xs uppercase text-slate-400">{k}</div>
            <div className="text-2xl font-bold text-white">
              {stats ? (stats as any)[k] : '—'}
            </div>
          </div>
        ))}
      </div>

      {/* Filter + reload */}
      <div className="glass-dark p-4 rounded-2xl flex flex-wrap items-center gap-3">
        <span className="text-sm text-slate-400">Filter:</span>
        {STATUS_OPTIONS.map((s) => (
          <button
            key={s}
            onClick={() => { setPage(0); setStatusFilter(s); }}
            className={`px-3 py-1 rounded-full text-sm transition ${
              statusFilter === s
                ? 'bg-purple-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {s}
          </button>
        ))}
        <button
          onClick={reload}
          className="ml-auto flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-slate-800 text-slate-300 hover:bg-slate-700"
        >
          <RefreshCcw className="w-4 h-4" /> Reload
        </button>
      </div>

      {error && (
        <div className="glass-dark p-4 rounded-xl border border-rose-500/40 text-rose-300 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" /> {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-slate-400">
          <Clock className="w-4 h-4 animate-spin" /> Loading…
        </div>
      )}

      {!loading && data && data.items.length === 0 && (
        <div className="glass-dark p-8 rounded-2xl text-center text-slate-400">
          No items in this view.
        </div>
      )}

      <div className="space-y-4">
        {data?.items.map((item) => (
          <ReviewItemCard key={item.id} item={item} onDecide={handleDecide} busy={busy} />
        ))}
      </div>

      {/* Pager */}
      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3 mt-4">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
          >
            <ChevronLeft className="w-4 h-4" /> Prev
          </button>
          <span className="text-sm text-slate-400">
            Page {page + 1} / {totalPages}
          </span>
          <button
            disabled={page + 1 >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
