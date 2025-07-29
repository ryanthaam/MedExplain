import { Shield, Database, CheckCircle } from "lucide-react";
import TextType from "./TextType";

export function SourceIcons() {
  const sources = [
    {
      icon: <Shield className="w-12 h-12 text-teal-500" />,
      title: "Multi-Source Verified",
      description: "Data from FDA, NLM, NCBI, and medical literature databases"
    },
    {
      icon: <Database className="w-12 h-12 text-teal-500" />,
      title: "Comprehensive Coverage",
      description: "Drug classes, interactions, chemical data, and clinical information"
    },
    {
      icon: <CheckCircle className="w-12 h-12 text-teal-500" />,
      title: "Enhanced Intelligence",
      description: "AI-powered analysis with plain English translation"
    }
  ];

  return (
    <section className="py-16 px-6 bg-slate-900">
      <div className="max-w-6xl mx-auto">
        <TextType 
          text="Trusted Sources"
          as="h2"
          className="text-3xl font-bold text-center mb-12 text-white"
          typingSpeed={80}
          initialDelay={300}
          loop={false}
          showCursor={true}
          cursorCharacter="|"
          cursorClassName="text-teal-400"
          startOnVisible={true}
        />
        <div className="grid md:grid-cols-3 gap-8">
          {sources.map((source, index) => (
            <div key={index} className="text-center p-6 bg-slate-800 rounded-xl">
              <div className="flex justify-center mb-4">
                {source.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2 text-white">{source.title}</h3>
              <p className="text-slate-400">{source.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}