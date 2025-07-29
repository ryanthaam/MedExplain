import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import TextType from "./TextType";

export function HeroSection() {
  const navigate = useNavigate();

  const handleStartChat = () => {
    navigate('/chat');
  };

  const heroMessages = [
    "Understand Medications Instantly",
    "Get FDA-Sourced Drug Information", 
    "Ask About Multiple Drugs at Once",
    "Medical Jargon Made Simple"
  ];

  return (
    <section className="text-center py-20 px-6 bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      <div className="h-20 mb-4">
        <TextType 
          text={heroMessages}
          as="h1"
          className="text-4xl md:text-6xl font-bold"
          typingSpeed={80}
          pauseDuration={2500}
          deletingSpeed={40}
          loop={true}
          showCursor={true}
          cursorCharacter="|"
          cursorClassName="text-teal-400"
          textColors={["#ffffff", "#14b8a6", "#ffffff", "#14b8a6"]}
        />
      </div>
      <TextType 
        text="AI-powered answers from trusted FDA sources"
        as="p"
        className="text-lg md:text-xl text-slate-400 mb-8"
        typingSpeed={60}
        initialDelay={1000}
        loop={false}
        showCursor={false}
      />
      <Button 
        onClick={handleStartChat}
        className="bg-teal-500 hover:bg-teal-400 text-black font-semibold px-6 py-3 rounded-xl transition"
      >
        Start Chatting
      </Button>
    </section>
  );
}