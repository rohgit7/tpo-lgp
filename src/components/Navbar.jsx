export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm px-8 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
  <span className="text-blue-600 text-2xl font-bold">Shakun&nbsp;</span>
  <span className="text-gray-800 text-2xl font-bold">AI&nbsp;</span>
  <span className="ml-1 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full font-medium">Financial Forensics</span>
</div>
      
        <a href="/"
        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
      >
        + Upload New File
      </a>
    </nav>
  );
}