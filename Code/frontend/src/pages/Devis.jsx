import { useState, useEffect } from 'react';

export default function Devis() {
  const [devis, setDevis]           = useState([]);
  const [alertes, setAlertes]       = useState([]);
  const [clarifs, setClarifs]       = useState([]);
  const [activeTab, setActiveTab]   = useState('devis');
  const [loading, setLoading]       = useState(true);
  const [running, setRunning]       = useState(false);
  const [runMsg, setRunMsg]         = useState(null);
  const [selected, setSelected]     = useState(null);

  const loadAll = () => {
    setLoading(true);
    Promise.all([
      fetch('/api/devis').then(r => r.json()),
      fetch('/api/devis/alertes').then(r => r.json()),
      fetch('/api/devis/clarifications').then(r => r.json()),
    ]).then(([d, a, c]) => {
      setDevis(Array.isArray(d) ? d : []);
      setAlertes(Array.isArray(a) ? a : []);
      setClarifs(Array.isArray(c) ? c : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  const handleRunFluxB = () => {
    setRunning(true);
    setRunMsg(null);
    fetch('/api/run-flux-b', { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        setRunning(false);
        if (data.error) {
          setRunMsg({ type: 'error', text: `Erreur : ${data.error}` });
        } else {
          setRunMsg({ type: 'success', text: `✓ Flux B terminé ! ${data.message}` });
          loadAll();
        }
        setTimeout(() => setRunMsg(null), 6000);
      })
      .catch(() => {
        setRunning(false);
        setRunMsg({ type: 'error', text: 'Impossible de joindre le backend.' });
      });
  };

  useEffect(() => { loadAll(); }, []);

  const tabs = [
    { id: 'devis',   label: 'Devis générés', count: devis.length,   icon: 'description' },
    { id: 'alertes', label: 'Alertes',        count: alertes.length, icon: 'warning',    urgent: alertes.length > 0 },
    { id: 'clarifs', label: 'À clarifier',    count: clarifs.length, icon: 'help_outline' },
  ];

  if (loading) {
    return (
      <main className="p-8 flex justify-center items-center h-[50vh]">
        <div className="flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-5xl text-primary animate-spin">sync</span>
          <p className="text-on-surface-variant font-medium">Chargement des devis...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="p-8 max-w-[1440px] w-full mx-auto">
      {/* Header */}
      <section className="mb-8 flex items-end justify-between">
        <div>
          <h3 className="text-[36px] font-bold text-on-surface leading-tight">Flux B — Devis</h3>
          <p className="text-[16px] text-on-surface-variant mt-2">
            Génération automatique de devis depuis les demandes en texte libre.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          {runMsg && (
            <span className={`text-xs font-semibold px-3 py-1 rounded-lg ${
              runMsg.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>{runMsg.text}</span>
          )}
          <button
            onClick={handleRunFluxB}
            disabled={running}
            className={`px-6 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
              running ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-primary text-white hover:opacity-90'
            }`}
          >
            <span className={`material-symbols-outlined text-[18px] ${running ? 'animate-spin' : ''}`}>
              {running ? 'sync' : 'play_arrow'}
            </span>
            {running ? 'Traitement en cours...' : 'Lancer Flux B'}
          </button>
        </div>
      </section>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <KpiCard label="Devis générés"    value={devis.length}   icon="description"  color="text-primary" />
        <KpiCard
          label="Volume TTC total"
          value={devis.length > 0
            ? `${devis.reduce((s, d) => s + (d.grand_total_ttc || 0), 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €`
            : '0,00 €'}
          icon="euro"
          color="text-green-600"
        />
        <KpiCard label="Lignes à clarifier" value={clarifs.length}  icon="help_outline" color="text-orange-500" />
        <KpiCard label="Alertes humaines"   value={alertes.length}  icon="warning"      color="text-red-500"    />
      </div>

      {/* Tabs */}
      <div className="flex gap-0 mb-6 border-b border-outline-variant">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold transition-all border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
            {tab.label}
            <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
              tab.urgent ? 'bg-red-100 text-red-700' : 'bg-surface-container text-on-surface-variant'
            }`}>{tab.count}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'devis' && (
        <DevisTab devis={devis} selected={selected} setSelected={setSelected} />
      )}
      {activeTab === 'alertes' && (
        <AlertesTab alertes={alertes} />
      )}
      {activeTab === 'clarifs' && (
        <ClarifTab clarifs={clarifs} />
      )}
    </main>
  );
}

// ─── Onglet Devis générés ───────────────────────────────────────────────────
function DevisTab({ devis, selected, setSelected }) {
  if (devis.length === 0) {
    return <EmptyState icon="description" message="Aucun devis généré. Lancez le Flux B pour commencer." />;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Liste devis */}
      <div className="lg:col-span-1 space-y-3 max-h-[600px] overflow-y-auto pr-1">
        {devis.map(d => (
          <button
            key={d.devis_id}
            onClick={() => setSelected(selected?.devis_id === d.devis_id ? null : d)}
            className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
              selected?.devis_id === d.devis_id
                ? 'border-primary bg-primary/5 shadow-md'
                : 'border-outline-variant bg-white hover:border-primary/40 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-sm font-bold text-on-surface">{d.devis_id}</p>
                <p className="text-xs text-on-surface-variant mt-0.5 truncate max-w-[160px]">{d.raison_sociale}</p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="text-sm font-bold text-primary">
                  {(d.grand_total_ttc || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  d.langue === 'EN' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                }`}>{d.langue}</span>
              </div>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-[11px] text-on-surface-variant">{d.date_devis}</span>
              {d.nb_lignes_clarifier > 0 && (
                <span className="text-[10px] bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded font-semibold">
                  {d.nb_lignes_clarifier} à clarifier
                </span>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Détail devis */}
      <div className="lg:col-span-2">
        {selected ? (
          <div className="bg-white border border-outline-variant rounded-xl p-6 shadow-sm">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h4 className="text-xl font-bold text-on-surface">{selected.devis_id}</h4>
                <p className="text-sm text-on-surface-variant mt-1">{selected.raison_sociale} · {selected.client_id}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                selected.langue === 'EN' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
              }`}>{selected.langue}</span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <InfoRow label="Date du devis"      value={selected.date_devis} />
              <InfoRow label="Valide jusqu'au"    value={selected.date_validite} />
              <InfoRow label="Lignes chiffrées"   value={selected.nb_lignes_chiffrees} />
              <InfoRow label="Lignes à clarifier" value={selected.nb_lignes_clarifier} />
            </div>

            <div className="bg-surface-container-low rounded-xl p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">Total HT</p>
                  <p className="text-lg font-bold text-on-surface">
                    {(selected.grand_total_ht || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                  </p>
                </div>
                <div>
                  <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">TVA</p>
                  <p className="text-lg font-bold text-on-surface">
                    {(selected.grand_total_tva || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                  </p>
                </div>
                <div className="bg-primary/10 rounded-lg p-2">
                  <p className="text-xs text-primary uppercase tracking-wider mb-1 font-semibold">Total TTC</p>
                  <p className="text-2xl font-bold text-primary">
                    {(selected.grand_total_ttc || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                  </p>
                </div>
              </div>
            </div>

            {selected.fichier_outbox && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-sm text-green-700">
                <span className="material-symbols-outlined text-[18px]">outbox</span>
                Courrier simulé : <span className="font-mono font-semibold">{selected.fichier_outbox}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full min-h-[300px] bg-white border border-outline-variant rounded-xl text-on-surface-variant">
            <div className="text-center">
              <span className="material-symbols-outlined text-4xl mb-2 block">touch_app</span>
              <p className="text-sm">Sélectionnez un devis pour voir le détail</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Onglet Alertes ──────────────────────────────────────────────────────────
function AlertesTab({ alertes }) {
  if (alertes.length === 0) {
    return <EmptyState icon="check_circle" message="Aucune alerte de validation humaine." success />;
  }

  const iconLabels = {
    SECURITE_IBAN:          'IBAN/RIB détecté',
    SECURITE_MANIPULATION:  'Tentative de manipulation',
    REMISE_HORS_GRILLE:     'Remise hors grille (R10)',
    CLIENT_INCONNU:         'Client inconnu / Prospect',
    MESSAGE_MIXTE_RECLAMATION: 'Message mixte (réclamation)',
  };

  return (
    <div className="space-y-4">
      {alertes.map((a, i) => (
        <div key={i} className={`flex gap-4 p-4 border-l-4 rounded-r-xl ${a.color}`}>
          <span className="material-symbols-outlined text-[22px] flex-shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>
            {a.icon}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-xs font-bold uppercase tracking-wide">
                {iconLabels[a.type_alerte] || a.type_alerte}
              </span>
              <span className="text-xs opacity-70">·</span>
              <span className="text-xs font-mono">{a.demande_id}</span>
              <span className="text-xs opacity-70">·</span>
              <span className="text-xs">{a.client_id}</span>
            </div>
            <p className="text-sm leading-snug">{a.detail}</p>
            <p className="text-xs opacity-60 mt-1">{a.horodatage}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Onglet Lignes à clarifier ───────────────────────────────────────────────
function ClarifTab({ clarifs }) {
  if (clarifs.length === 0) {
    return <EmptyState icon="check_circle" message="Toutes les lignes ont été identifiées dans le catalogue." success />;
  }

  // Grouper par demande_id
  const grouped = clarifs.reduce((acc, c) => {
    if (!acc[c.demande_id]) acc[c.demande_id] = [];
    acc[c.demande_id].push(c);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([demande_id, lignes]) => (
        <div key={demande_id} className="bg-white border border-outline-variant rounded-xl overflow-hidden shadow-sm">
          <div className="px-5 py-3 bg-orange-50 border-b border-orange-100 flex items-center gap-3">
            <span className="material-symbols-outlined text-orange-500 text-[18px]">help_outline</span>
            <p className="text-sm font-bold text-orange-700">{demande_id}</p>
            <span className="text-xs text-orange-600">— {lignes[0].raison_sociale || lignes[0].client_id}</span>
            <span className="ml-auto text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full font-semibold">
              {lignes.length} ligne{lignes.length > 1 ? 's' : ''}
            </span>
          </div>
          <div className="divide-y divide-outline-variant">
            {lignes.map((l, i) => (
              <div key={i} className="px-5 py-3 flex items-center gap-4">
                <span className="material-symbols-outlined text-on-surface-variant text-[16px]">inventory_2</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-on-surface">« {l.libelle_demande} »</p>
                  <p className="text-xs text-on-surface-variant mt-0.5">{l.motif}</p>
                </div>
                <span className="text-xs text-on-surface-variant font-mono">Qté : {l.qte}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Composants utilitaires ──────────────────────────────────────────────────
function KpiCard({ label, value, icon, color }) {
  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-sm">
      <p className="text-[11px] font-semibold tracking-wider text-on-surface-variant uppercase mb-2">{label}</p>
      <div className="flex items-center justify-between">
        <p className={`text-[22px] font-bold ${color || 'text-on-surface'}`}>{value}</p>
        <span className={`material-symbols-outlined ${color || 'text-on-surface-variant'}`}>{icon}</span>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="bg-surface-container-low rounded-lg p-3">
      <p className="text-[10px] text-on-surface-variant uppercase tracking-wider mb-1">{label}</p>
      <p className="text-sm font-semibold text-on-surface">{value ?? '—'}</p>
    </div>
  );
}

function EmptyState({ icon, message, success }) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 text-center rounded-xl border ${
      success ? 'border-green-200 bg-green-50' : 'border-outline-variant bg-white'
    }`}>
      <span className={`material-symbols-outlined text-5xl mb-3 ${success ? 'text-green-500' : 'text-on-surface-variant'}`}
        style={{ fontVariationSettings: "'FILL' 1" }}>
        {icon}
      </span>
      <p className={`text-sm font-medium ${success ? 'text-green-700' : 'text-on-surface-variant'}`}>{message}</p>
    </div>
  );
}
