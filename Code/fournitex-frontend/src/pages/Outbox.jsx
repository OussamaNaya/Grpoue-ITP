import { useState, useEffect } from 'react';

export default function Outbox() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedRelance, setSelectedRelance] = useState(null);
  const [relances, setRelances] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const handlePreview = (relance) => {
    setSelectedRelance(relance);
    setModalOpen(true);
  };

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-[36px] font-bold text-on-surface">Outbox - Relances</h1>
          <p className="text-on-surface-variant">{relances.length} actions en attente de validation avant expédition.</p>
        </div>
        <button className="bg-primary text-white px-6 py-2 rounded-lg font-semibold flex items-center gap-2">
          <span className="material-symbols-outlined">send</span>
          Tout Envoyer
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8">Chargement...</div>
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
                <th className="px-6 py-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {relances.map((rel, idx) => (
                <tr key={idx} className="hover:bg-blue-50/50 transition-colors">
                  <td className="px-6 py-4 font-semibold">{rel.client}</td>
                  <td className="px-4 py-4">{rel.id}</td>
                  <td className="px-4 py-4 font-semibold text-gray-700">{rel.retard}</td>
                  <td className="px-4 py-4">
                    <span className={`px-2 py-1 rounded-md text-[10px] font-bold ${rel.badgeColor}`}>{rel.niveau}</span>
                  </td>
                  <td className="px-4 py-4 font-semibold">{rel.montant}</td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => handlePreview(rel)} className="text-primary hover:text-blue-800 text-sm font-semibold flex items-center justify-end gap-1 ml-auto">
                      <span className="material-symbols-outlined text-[18px]">visibility</span>
                      Prévisualiser
                    </button>
                  </td>
                </tr>
              ))}
              {relances.length === 0 && (
                <tr><td colSpan="6" className="text-center py-8">Aucune relance à envoyer.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="bg-gray-50 px-6 py-4 border-b flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 font-semibold uppercase">Prévisualisation Email</p>
                <h3 className="font-bold text-lg">{selectedRelance?.objet}</h3>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-gray-400 hover:text-gray-800">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="p-6 text-sm text-gray-700 whitespace-pre-line leading-relaxed">
              {selectedRelance?.message}
            </div>
            <div className="bg-gray-50 px-6 py-4 border-t flex justify-end gap-3">
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 text-gray-600 font-semibold hover:bg-gray-200 rounded-lg transition-colors">Annuler</button>
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 bg-primary text-white font-semibold rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors">
                <span className="material-symbols-outlined text-[18px]">send</span> Envoyer
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
