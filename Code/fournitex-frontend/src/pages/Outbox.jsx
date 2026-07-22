import { useState, useEffect } from 'react';

export default function Outbox() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedRelance, setSelectedRelance] = useState(null);
  const [relances, setRelances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sentIds, setSentIds] = useState(new Set());
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetch('/api/outbox')
      .then(res => res.json())
      .then(data => {
        setRelances(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load outbox", err);
        setLoading(false);
      });
  }, []);

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(null), 4000);
  };

  const handleSend = (rel, idx) => {
    setSentIds(prev => new Set([...prev, idx]));
    showToast(`✓ Cette relance pour ${rel.client} (${rel.id}) a été envoyée avec succès.`);
    setModalOpen(false);
  };

  const handleSendAll = () => {
    const pending = relances
      .map((_, i) => i)
      .filter(i => !sentIds.has(i));
    setSentIds(prev => new Set([...prev, ...pending]));
    showToast(`✓ ${pending.length} relance(s) ont été envoyées avec succès.`);
  };

  const handlePreview = (relance) => {
    setSelectedRelance(relance);
    setModalOpen(true);
  };

  const pendingCount = relances.filter((_, i) => !sentIds.has(i)).length;

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      {/* Toast notification */}
      {toast && (
        <div className="fixed top-6 right-6 z-[100] max-w-md bg-green-600 text-white px-5 py-4 rounded-xl shadow-2xl flex items-start gap-3 animate-pulse">
          <span className="material-symbols-outlined text-[20px] mt-0.5" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
          <p className="text-sm font-medium leading-relaxed">{toast}</p>
          <button onClick={() => setToast(null)} className="ml-auto text-white/70 hover:text-white">
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      )}

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-[36px] font-bold text-on-surface">Outbox — Relances</h1>
          <p className="text-on-surface-variant mt-1">
            <span className="font-semibold text-primary">{pendingCount}</span> relances en attente ·{' '}
            <span className="font-semibold text-green-600">{sentIds.size}</span> envoyées
          </p>
        </div>
        <button
          onClick={handleSendAll}
          disabled={pendingCount === 0}
          className={`px-6 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all ${
            pendingCount === 0
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:opacity-90'
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">send</span>
          Tout Envoyer {pendingCount > 0 && `(${pendingCount})`}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8 text-on-surface-variant">Chargement...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-outline-variant overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-[12px] uppercase text-gray-500">
              <tr>
                <th className="px-6 py-4 font-bold">Client</th>
                <th className="px-4 py-4 font-bold">Facture</th>
                <th className="px-4 py-4 font-bold">Retard</th>
                <th className="px-4 py-4 font-bold">Niveau</th>
                <th className="px-4 py-4 font-bold">Montant</th>
                <th className="px-4 py-4 font-bold">Statut</th>
                <th className="px-6 py-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {relances.map((rel, idx) => {
                const isSent = sentIds.has(idx);
                return (
                  <tr key={idx} className={`transition-colors ${isSent ? 'bg-green-50' : 'hover:bg-blue-50/50'}`}>
                    <td className={`px-6 py-4 font-semibold ${isSent ? 'text-gray-400' : ''}`}>{rel.client}</td>
                    <td className={`px-4 py-4 ${isSent ? 'text-gray-400' : ''}`}>{rel.id}</td>
                    <td className={`px-4 py-4 font-semibold ${isSent ? 'text-gray-400' : 'text-gray-700'}`}>{rel.retard}</td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-1 rounded-md text-[10px] font-bold ${isSent ? 'bg-gray-100 text-gray-400' : rel.badgeColor}`}>
                        {rel.niveau}
                      </span>
                    </td>
                    <td className={`px-4 py-4 font-semibold ${isSent ? 'text-gray-400' : ''}`}>{rel.montant}</td>
                    <td className="px-4 py-4">
                      {isSent ? (
                        <span className="flex items-center gap-1 text-green-600 text-xs font-semibold">
                          <span className="material-symbols-outlined text-[16px]" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
                          Envoyée
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">En attente</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handlePreview(rel)}
                          className="text-primary hover:text-blue-800 text-sm font-semibold flex items-center gap-1"
                        >
                          <span className="material-symbols-outlined text-[18px]">visibility</span>
                        </button>
                        {!isSent ? (
                          <button
                            onClick={() => handleSend(rel, idx)}
                            className="bg-primary text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
                          >
                            <span className="material-symbols-outlined text-[14px]">send</span>
                            Envoyer
                          </button>
                        ) : (
                          <span className="text-xs text-gray-300 px-3 py-1.5">—</span>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
              {relances.length === 0 && (
                <tr>
                  <td colSpan="7" className="text-center py-12 text-gray-400">Aucune relance à envoyer.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Preview Modal */}
      {modalOpen && selectedRelance && (
        <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="bg-gray-50 px-6 py-4 border-b flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Prévisualisation Email</p>
                <h3 className="font-bold text-lg mt-0.5">{selectedRelance.objet}</h3>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-gray-400 hover:text-gray-800 transition-colors">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="p-6 text-sm text-gray-700 whitespace-pre-line leading-relaxed min-h-[200px]">
              {selectedRelance.message}
            </div>
            <div className="bg-gray-50 px-6 py-4 border-t flex justify-end gap-3">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 text-gray-600 font-semibold hover:bg-gray-200 rounded-lg transition-colors"
              >
                Fermer
              </button>
              {!sentIds.has(relances.indexOf(selectedRelance)) ? (
                <button
                  onClick={() => handleSend(selectedRelance, relances.indexOf(selectedRelance))}
                  className="px-4 py-2 bg-primary text-white font-semibold rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
                >
                  <span className="material-symbols-outlined text-[18px]">send</span>
                  Envoyer
                </button>
              ) : (
                <span className="px-4 py-2 bg-green-100 text-green-700 font-semibold rounded-lg flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
                  Déjà envoyée
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
