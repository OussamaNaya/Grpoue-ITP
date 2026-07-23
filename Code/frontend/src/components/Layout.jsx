import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'dashboard' },
    { name: 'Outbox', path: '/outbox', icon: 'outbox' },
    { name: 'Anomalies Center', path: '/anomalies', icon: 'warning' },
    { name: 'Devis (Flux B)', path: '/devis', icon: 'request_quote' },
  ];

  return (
    <div className="bg-background text-on-surface antialiased">
      {/* SideNavBar */}
      <aside className="w-[260px] h-screen fixed left-0 top-0 bg-surface-container-low border-r border-outline-variant flex flex-col pt-6 pb-4 z-50">
        <div className="px-6 mb-8">
          <h1 className="text-[24px] font-bold text-primary leading-tight">Fournitex ADV</h1>
          <p className="text-[12px] text-on-surface-variant font-semibold mt-1 tracking-wider">COLLECTION & RECOVERY</p>
        </div>
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-6 py-3 transition-all duration-200 ${isActive
                  ? 'border-l-4 border-primary bg-primary-container/20 text-primary font-medium'
                  : 'text-on-surface hover:bg-surface-container-high'
                  }`}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span className="text-[16px]">{item.name}</span>
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto px-6 border-t border-outline-variant pt-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
              SA
            </div>
            <div>
              <p className="text-[14px] font-semibold">Service ADV</p>
              <p className="text-[12px] text-on-surface-variant">Manager</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="ml-[260px] min-h-screen flex flex-col">
        {/* TopNavBar */}
        <header className="flex justify-between items-center w-full px-lg h-16 sticky top-0 bg-surface border-b border-outline-variant z-40">
          <div className="flex items-center gap-lg flex-1">
            <h2 className="text-[18px] font-semibold text-on-surface">Bonjour, Service ADV</h2>
            <div className="relative w-full max-w-md ml-lg cursor-pointer ml-12">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
              <input
                className="w-full bg-surface-container-low border border-outline-variant rounded-lg py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                placeholder="Rechercher un dossier, une facture..."
                type="text"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-surface-container rounded-full text-on-surface-variant transition-all duration-200">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 hover:bg-surface-container rounded-full text-on-surface-variant transition-all duration-200">
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </header>

        {children}
      </div>
    </div>
  );
}
