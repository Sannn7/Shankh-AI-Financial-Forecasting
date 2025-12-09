
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/utils';

export default function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        "relative inline-flex h-10 w-20 items-center justify-center rounded-full bg-muted p-1 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
        className
      )}
      aria-label="Toggle theme"
    >
      <span
        className={cn(
          "absolute left-1 flex h-8 w-8 items-center justify-center rounded-full bg-background shadow-md transition-transform duration-300",
          theme === "dark" ? "translate-x-10" : "translate-x-0"
        )}
      >
        {theme === "dark" ? (
          <Moon className="h-5 w-5 text-primary animate-fade-in" />
        ) : (
          <Sun className="h-5 w-5 text-warning animate-fade-in" />
        )}
      </span>
      <span className={cn("sr-only", theme === "dark" ? "opacity-0" : "opacity-100")}>
        Light mode
      </span>
      <span className={cn("sr-only", theme === "dark" ? "opacity-100" : "opacity-0")}>
        Dark mode
      </span>
    </button>
  );
}
