import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState(null);

  const loadStats = () => {
    setLoading(true);
    fetch('/api/dashboard-stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load stats", err);
        setLoading(false);
      });
  };

  const handleRunPipeline = () => {
    setRunning(true);
    setRunMessage(null);
    fetch('/api/run-pipeline', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setRunning(false);
        if (data.error) {
          setRunMessage({ type: 'error', text: `Erreur: ${data.error}` });
        } else {
          setRunMessage({ type: 'success', text: `✓ Pipeline terminé ! ${data.message}` });
          loadStats();
        }
        setTimeout(() => setRunMessage(null), 5000);
      })
      .catch(err => {
        setRunning(false);
        setRunMessage({ type: 'error', text: 'Impossible de joindre le backend.' });
      });
  };

  useEffect(() => { loadStats(); }, []);

  if (loading) {
    return <main className="p-8 max-w-[1440px] w-full mx-auto flex justify-center items-center h-[50vh]">Chargement...</main>;
  }

  if (!stats) {
    return <main className="p-8 max-w-[1440px] w-full mx-auto flex justify-center items-center h-[50vh] text-red-500">Erreur de chargement des données. L'API backend est-elle lancée ?</main>;
  }

  // Calculate percentages for distribution chart
  const totalRelances = stats.relances_a_envoyer || 1;
  const getPercent = (count) => `${((count || 0) / totalRelances * 100).toFixed(0)}%`;

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      {/* Welcome Section */}
      <section className="mb-8 flex items-end justify-between">
        <div>
          <h3 className="text-[36px] font-bold text-on-surface leading-tight">Tableau de bord</h3>
          <p className="text-[16px] text-on-surface-variant mt-2">Suivi en temps réel de votre poste client et des actions de recouvrement.</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          {runMessage && (
            <span className={`text-xs font-semibold px-3 py-1 rounded-lg ${
              runMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>{runMessage.text}</span>
          )}
          <button
            onClick={handleRunPipeline}
            disabled={running}
            className={`px-6 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
              running ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-primary text-white hover:opacity-90'
            }`}
          >
            <span className={`material-symbols-outlined text-[18px] ${running ? 'animate-spin' : ''}`}>
              {running ? 'sync' : 'play_arrow'}
            </span>
            {running ? 'Calcul en cours...' : 'Lancer Calculs'}
          </button>
        </div>
      </section>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Factures en retard" value={stats.factures_en_retard} icon="trending_up" detail="+0%" color="text-error" />
        <StatCard title="Montant à recouvrer" value={stats.montant_a_recouvrer} icon="payments" detail="En attente" color="text-primary" />
        <StatCard title="Anomalies bloquées" value={stats.anomalies_bloquees} badge={stats.anomalies_bloquees > 0 ? "CRITICAL" : "OK"} badgeColor={stats.anomalies_bloquees > 0 ? "bg-error-container text-on-error-container" : "bg-green-100 text-green-800"} color="text-error" />
        <StatCard title="Relances à envoyer" value={stats.relances_a_envoyer} icon="history" detail="Aujourd'hui" color="text-tertiary-container" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Distribution Chart Card */}
        <div className="lg:col-span-7 bg-white p-6 rounded-xl shadow-sm border border-outline-variant">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h5 className="text-[18px] font-semibold text-on-surface">Répartition des retards</h5>
              <p className="text-[14px] text-on-surface-variant">Volume par niveau de relance</p>
            </div>
          </div>
          <div className="space-y-6">
            <ProgressBar label="Relance 1" count={`${stats.repartition['RELANCE_1'] || 0} dossiers`} percent={getPercent(stats.repartition['RELANCE_1'])} colorClass="bg-blue-500" />
            <ProgressBar label="Relance 2" count={`${stats.repartition['RELANCE_2'] || 0} dossiers`} percent={getPercent(stats.repartition['RELANCE_2'])} colorClass="bg-orange-400" />
            <ProgressBar label="Relance 3" count={`${stats.repartition['RELANCE_3'] || 0} dossiers`} percent={getPercent(stats.repartition['RELANCE_3'])} colorClass="bg-red-500" />
            <ProgressBar label="Recouvrement contentieux" count={`${stats.repartition['TRANSFERT_RECOUVREMENT'] || 0} dossiers`} percent={getPercent(stats.repartition['TRANSFERT_RECOUVREMENT'])} colorClass="bg-gray-800" />
          </div>
        </div>

        {/* Recent Activity / Anomalies */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-outline-variant flex-1">
            <h5 className="text-[18px] font-semibold text-on-surface mb-4">Aperçu Anomalies</h5>
            <div className="space-y-4">
              {stats.anomalies_bloquees > 0 ? (
                <AlertCard icon="warning" title={`${stats.anomalies_bloquees} anomalies détectées`} subtitle="Action requise dans le centre des anomalies" colorClass="bg-red-50 border-red-500 text-red-700" />
              ) : (
                <AlertCard icon="check_circle" title="Aucune anomalie" subtitle="Toutes les données sont saines" colorClass="bg-green-50 border-green-500 text-green-700" />
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

function StatCard({ title, value, icon, detail, badge, badgeColor, color }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-outline-variant">
      <p className="text-[12px] font-semibold tracking-wider text-on-surface-variant uppercase mb-2">{title}</p>
      <div className="flex items-end justify-between">
        <h4 className={`text-[24px] font-bold ${color || 'text-on-surface'}`}>{value}</h4>
        {badge ? (
           <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${badgeColor}`}>{badge}</span>
        ) : (
          <span className={`text-[12px] flex items-center font-semibold ${color}`}>
            <span className="material-symbols-outlined text-[14px] mr-1">{icon}</span>
            {detail}
          </span>
        )}
      </div>
    </div>
  );
}

function ProgressBar({ label, count, percent, colorClass }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs font-semibold text-on-surface-variant">
        <span>{label}</span>
        <span>{count}</span>
      </div>
      <div className="w-full h-8 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${colorClass} rounded-full transition-all duration-1000 ease-out`} style={{ width: percent }}></div>
      </div>
    </div>
  );
}

function AlertCard({ icon, title, subtitle, colorClass }) {
  return (
    <div className={`flex gap-4 p-3 border-l-4 rounded-r-lg ${colorClass}`}>
      <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>{icon}</span>
      <div>
        <p className="text-[14px] font-bold">{title}</p>
        <p className="text-xs opacity-80">{subtitle}</p>
      </div>
    </div>
  );
}
