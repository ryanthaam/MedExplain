import { Github, Mail, Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-slate-950 text-white py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">MedExplain</h3>
            <p className="text-slate-400 mb-4">
              Making medication information accessible through AI-powered FDA data analysis.
            </p>
            <div className="flex space-x-4">
              <Github className="w-5 h-5 text-slate-400 hover:text-white cursor-pointer" />
              <Mail className="w-5 h-5 text-slate-400 hover:text-white cursor-pointer" />
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Features</h4>
            <ul className="space-y-2 text-slate-400">
              <li>Multi-drug queries</li>
              <li>Plain English translation</li>
              <li>Real-time FDA data</li>
              <li>Safety warnings</li>
              <li>Drug interactions</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Data Sources</h4>
            <ul className="space-y-2 text-slate-400">
              <li><a href="https://www.fda.gov" className="hover:text-white">FDA.gov</a></li>
              <li><a href="https://open.fda.gov" className="hover:text-white">OpenFDA API</a></li>
              <li><a href="https://dailymed.nlm.nih.gov" className="hover:text-white">DailyMed NLM</a></li>
              <li><a href="https://rxnav.nlm.nih.gov" className="hover:text-white">RxNorm NLM</a></li>
              <li><a href="https://pubchem.ncbi.nlm.nih.gov" className="hover:text-white">PubChem NCBI</a></li>
              <li><span className="text-slate-500">+ Medical Literature</span></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-slate-400 text-sm">
            © 2024 MedExplain. Educational use only. Not medical advice.
          </p>
          <div className="flex items-center mt-4 md:mt-0">
            <Shield className="w-4 h-4 text-teal-500 mr-2" />
            <span className="text-sm text-slate-400">FDA Data Sources</span>
          </div>
        </div>
      </div>
    </footer>
  );
}