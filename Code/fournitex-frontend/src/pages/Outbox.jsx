import { useState } from 'react';

export default function Outbox() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedRelance, setSelectedRelance] = useState(null);

  const relances = [
    { client: 'Logistique Grand Est', id: '#FA-2023-445', retard: '45 jours', niveau: 'RELANCE 3', montant: '4 250,00 €', badgeColor: 'bg-red-100 text-red-800' },
    { client: 'Tech Innovations SAS', id: '#FA-2023-450', retard: '18 jours', niveau: 'RELANCE 1', montant: '1 120,50 €', badgeColor: 'bg-yellow-100 text-yellow-800' },
    { client: 'Menuiserie Lacan', id: '#FA-2023-455', retard: '32 jours', niveau: 'RELANCE 2', montant: '890,00 €', badgeColor: 'bg-orange-100 text-orange-800' },
  ];

  const handlePreview = (relance) => {
    setSelectedRelance(relance);
    setModalOpen(true);
  };

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-[36px] font-bold text-on-surface">Outbox - Relances</h1>
          <p className="text-on-surface-variant">27 actions en attente de validation avant expédition.</p>
        </div>
        <button className="bg-primary text-white px-6 py-2 rounded-lg font-semibold flex items-center gap-2">
          <span className="material-symbols-outlined">send</span>
          Tout Envoyer
        </button>
      </div>

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
              <tr key={idx} className="hover:bg-blue-50/50">
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
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="bg-gray-50 px-6 py-4 border-b flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 font-semibold uppercase">Prévisualisation Email</p>
                <h3 className="font-bold text-lg">Objet: Relance - Facture {selectedRelance?.id} impayée</h3>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-gray-400 hover:text-gray-800">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="p-6 text-sm text-gray-700 whitespace-pre-line">
              {`Bonjour,

Sauf erreur de notre part, la facture ${selectedRelance?.id} d'un montant de ${selectedRelance?.montant} reste en attente de règlement. 
Il s'agit sans doute d'un oubli — merci de le régulariser sous 8 jours.

Bien cordialement,
Service ADV Fournitex`}
            </div>
            <div className="bg-gray-50 px-6 py-4 border-t flex justify-end gap-3">
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 text-gray-600 font-semibold hover:bg-gray-200 rounded-lg">Annuler</button>
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 bg-primary text-white font-semibold rounded-lg flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">send</span> Envoyer
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
