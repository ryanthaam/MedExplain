import { AlertTriangle, Heart, Users } from "lucide-react";
import TextType from "./TextType";

export function TrustIndicators() {
  const indicators = [
    {
      icon: <AlertTriangle className="w-8 h-8 text-yellow-500" />,
      title: "Safety First",
      description: "Comprehensive safety warnings and drug interaction checks"
    },
    {
      icon: <Heart className="w-8 h-8 text-red-500" />,
      title: "Healthcare Focus", 
      description: "Always encourages consultation with healthcare professionals"
    },
    {
      icon: <Users className="w-8 h-8 text-blue-500" />,
      title: "For Everyone",
      description: "Medical information made accessible to all users"
    }
  ];

  return (
    <section className="py-16 px-6 bg-slate-800">
      <div className="max-w-6xl mx-auto">
        <TextType 
          text="Why Trust MedExplain?"
          as="h2"
          className="text-3xl font-bold text-center mb-12 text-white"
          typingSpeed={80}
          initialDelay={500}
          loop={false}
          showCursor={true}
          cursorCharacter="|"
          cursorClassName="text-teal-400"
          startOnVisible={true}
        />
        <div className="grid md:grid-cols-3 gap-8">
          {indicators.map((indicator, index) => (
            <div key={index} className="text-center p-6">
              <div className="flex justify-center mb-4">
                {indicator.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2 text-white">{indicator.title}</h3>
              <p className="text-slate-400">{indicator.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-12 p-6 bg-slate-900 rounded-xl border border-yellow-500/20">
          <div className="flex items-center justify-center mb-4">
            <AlertTriangle className="w-6 h-6 text-yellow-500 mr-2" />
            <span className="text-yellow-500 font-semibold">Important Disclaimer</span>
          </div>
          <p className="text-slate-300 text-center">
            MedExplain provides educational information only and is not a substitute for professional medical advice. 
            Always consult your healthcare provider for medical decisions.
          </p>
        </div>
      </div>
    </section>
  );
}