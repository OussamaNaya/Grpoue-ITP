import { useState, useEffect } from 'react';

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/anomalies')
      .then(res => res.json())
      .then(data => {
        setAnomalies(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load anomalies", err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      <div className="mb-8">
        <h1 className="text-[36px] font-bold text-on-surface">Centre des Anomalies</h1>
        <p className="text-on-surface-variant">Gérez les factures bloquées par le système nécessitant une intervention manuelle.</p>
      </div>

      {loading ? (
        <div className="flex justify-center p-8">Chargement...</div>
      ) : anomalies.length === 0 ? (
        <div className="bg-green-50 text-green-700 p-6 rounded-lg text-center font-semibold">Aucune anomalie détectée dans le flux de données.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {anomalies.map((anom, idx) => (
            <div key={idx} className={`p-6 rounded-xl border-l-4 shadow-sm bg-white border border-gray-200 ${anom.color.split(' ')[1]}`}>
              <div className="flex items-start gap-4 mb-4">
                <span className={`material-symbols-outlined text-[24px] ${anom.color.split(' ')[2]}`}>{anom.icon}</span>
                <div>
                  <h3 className={`font-bold text-[16px] ${anom.color.split(' ')[2]}`}>{anom.type}</h3>
                  <p className="text-sm text-gray-600 mt-1">Facture: {anom.facture_id}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                <button className={`px-4 py-1.5 rounded-lg text-sm font-semibold ${anom.color.split(' ')[0]} ${anom.color.split(' ')[2]} hover:opacity-80 transition-opacity`}>
                  Résoudre
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
