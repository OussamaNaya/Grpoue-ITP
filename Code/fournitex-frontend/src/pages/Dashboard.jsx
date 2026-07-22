import { useState } from 'react';

export default function Dashboard() {
  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      {/* Welcome Section */}
      <section className="mb-8 flex items-end justify-between">
        <div>
          <h3 className="text-[36px] font-bold text-on-surface leading-tight">Tableau de bord</h3>
          <p className="text-[16px] text-on-surface-variant mt-2">Suivi en temps réel de votre poste client et des actions de recouvrement.</p>
        </div>
        <button className="bg-primary text-white px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition-all flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">add</span>
          Nouvelle Action
        </button>
      </section>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Factures en retard" value="65" icon="trending_up" detail="+12%" color="text-error" />
        <StatCard title="Montant à recouvrer" value="45 200 €" icon="payments" detail="En attente" color="text-primary" />
        <StatCard title="Anomalies bloquées" value="7" badge="CRITICAL" badgeColor="bg-error-container text-on-error-container" color="text-error" />
        <StatCard title="Relances à envoyer" value="27" icon="history" detail="Aujourd'hui" color="text-tertiary-container" />
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
            <ProgressBar label="Relance 1" count="13 dossiers" percent="48%" colorClass="bg-blue-500" />
            <ProgressBar label="Relance 2" count="4 dossiers" percent="15%" colorClass="bg-orange-400" />
            <ProgressBar label="Relance 3" count="6 dossiers" percent="22%" colorClass="bg-red-500" />
            <ProgressBar label="Recouvrement contentieux" count="4 dossiers" percent="15%" colorClass="bg-gray-800" />
          </div>
        </div>

        {/* Recent Activity / Anomalies */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-outline-variant flex-1">
            <h5 className="text-[18px] font-semibold text-on-surface mb-4">Alertes Anomalies</h5>
            <div className="space-y-4">
              <AlertCard icon="warning" title="IBAN Invalide - Facture #FA-2023-98" subtitle="Société Durant & Fils" colorClass="bg-red-50 border-red-500 text-red-700" />
              <AlertCard icon="info" title="Adresse non vérifiée" subtitle="Alpha Tech Corp" colorClass="bg-blue-50 border-blue-500 text-blue-700" />
            </div>
            <button className="w-full mt-4 text-primary text-sm font-semibold py-2 rounded-lg hover:bg-gray-50">Voir toutes les anomalies</button>
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
