interface CommandBarProps {
  onSelectCommand: (command: string) => void;
  isLoading: boolean;
}

export function CommandBar({ onSelectCommand, isLoading }: CommandBarProps) {
  const commands = [
    { 
      cmd: '/compare', 
      description: 'Compare two medications',
      example: '/compare Ibuprofen vs Acetaminophen'
    },
    { 
      cmd: '/interactions', 
      description: 'Check drug interactions',
      example: '/interactions Warfarin and Aspirin'
    },
    { 
      cmd: '/explain', 
      description: 'Get detailed explanation',
      example: '/explain how does Metformin work'
    },
    { 
      cmd: '/dosage', 
      description: 'Get dosage information',
      example: '/dosage Ibuprofen for adults'
    }
  ];

  return (
    <div className="py-2">
      <div className="flex gap-3 text-sm text-slate-400 mb-2">
        <span className="font-semibold">Quick Commands:</span>
      </div>
      <div className="flex gap-2 flex-wrap">
        {commands.map((command, i) => (
          <button
            key={i}
            onClick={() => !isLoading && onSelectCommand(command.example)}
            disabled={isLoading}
            className="text-teal-400 hover:text-teal-300 disabled:text-slate-500 disabled:cursor-not-allowed text-sm transition-colors"
            title={command.description}
          >
            {command.cmd}
          </button>
        ))}
      </div>
    </div>
  );
}