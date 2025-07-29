interface SuggestedPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  isLoading: boolean;
}

export function SuggestedPrompts({ onSelectPrompt, isLoading }: SuggestedPromptsProps) {
  const prompts = [
    "What are the side effects of Ibuprofen?",
    "Can I take Acetaminophen with Amoxicillin?",
    "What is Metformin used for?",
    "Interactions between Aspirin and Warfarin",
    "What does Lisinopril do?",
    "Side effects of Sertraline",
    "Can I take Omeprazole daily?",
    "What is the difference between brand and generic drugs?"
  ];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      {prompts.map((prompt, i) => (
        <button 
          key={i} 
          onClick={() => !isLoading && onSelectPrompt(prompt)}
          disabled={isLoading}
          className="bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors"
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}