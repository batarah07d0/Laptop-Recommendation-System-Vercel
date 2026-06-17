import { useState } from "react";
import About from "./pages/About";
import Home from "./pages/Home";
import Result from "./pages/Result";

export default function App() {
  const [currentView, setCurrentView] = useState("home");
  const [results, setResults] = useState(null);

  const navigateTo = (view) => {
    // Jika user menekan logo "LaptopRec" SAAT sedang di halaman Home, barulah reset pencarian
    if (view === "home" && currentView === "home") {
      setResults(null);
    }
    setCurrentView(view);
    window.scrollTo(0, 0);
  };

  const handleSearchResults = (data) => {
    setResults(data);
    window.scrollTo(0, 0);
  };

  return (
    <div className="bg-slate-50 font-sans text-slate-800 min-h-screen flex flex-col">
      {/* NAVBAR */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Tombol Home (LaptopRec) */}
            <button
              onClick={() => navigateTo("home")}
              className={`text-2xl font-bold cursor-pointer transition-all duration-300 ${
                currentView === "home"
                  ? "text-blue-600 hover:text-blue-800!"
                  : "text-slate-800 hover:text-blue-600!"
              }`}
            >
              LaptopRec
            </button>

            {/* Tombol About (Tentang Sistem) */}
            <button
              onClick={() => navigateTo("about")}
              className={`font-bold cursor-pointer transition-all duration-300 ${
                currentView === "about"
                  ? "text-blue-600 hover:text-blue-800!"
                  : "text-slate-800 hover:text-blue-600!"
              }`}
            >
              Tentang Sistem
            </button>
          </div>
        </div>
      </nav>

      {/* KONTEN DINAMIS (PAGES) */}
      <main className="py-5 flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {currentView === "about" && <About onNavigate={navigateTo} />}
          {currentView === "home" && !results && (
            <Home onSearchResults={handleSearchResults} />
          )}
          {currentView === "home" && results && (
            <Result results={results} onBack={() => setResults(null)} />
          )}
        </div>
      </main>

      {/* FOOTER */}
      <footer className="bg-white mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-slate-500 font-medium">
            &copy; {new Date().getFullYear()} Sistem Rekomendasi Laptop - Batara
            Hotdo Horas Simbolon (00000078626) All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
