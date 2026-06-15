import { useState } from "react";

export default function InfoTooltip({ text }) {
  const [show, setShow] = useState(false);

  return (
    <div
      className="relative inline-block ml-1.5"
      onMouseEnter={() => {
        if (window.innerWidth >= 768) setShow(true);
      }}
      onMouseLeave={() => {
        if (window.innerWidth >= 768) setShow(false);
      }}
      onClick={(e) => {
        if (window.innerWidth < 768) {
          e.stopPropagation();
          setShow(!show);
        }
      }}
    >
      {/* Ikon i persis dari home.blade.php */}
      <button
        type="button"
        className="text-gray-400 hover:text-blue-600 focus:outline-none flex items-center"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clipRule="evenodd"
          ></path>
        </svg>
      </button>

      {/* Kotak Tooltip persis dari desain home.blade.php */}
      {show && (
        <div className="absolute z-50 w-64 sm:w-64 p-3 text-xs leading-relaxed text-white bg-gray-800 rounded-lg shadow-xl bottom-full left-1/2 transform -translate-x-1/2 mb-2">
          <div dangerouslySetInnerHTML={{ __html: text }} />
        </div>
      )}
    </div>
  );
}
