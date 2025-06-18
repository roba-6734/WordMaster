import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Volume2, RotateCcw } from 'lucide-react';
import './AnimatedFlashcard.css'; // We'll create this CSS file

const AnimatedFlashcard = ({ word, onFlip, isFlipped, onPronounce }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const handleFlip = () => {
    if (isAnimating) return; // Prevent multiple clicks during animation
    
    setIsAnimating(true);
    onFlip();
    
    // Reset animation state after animation completes
    setTimeout(() => {
      setIsAnimating(false);
    }, 600); // Match CSS animation duration
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flashcard-container" onClick={handleFlip}>
      <div className={`flashcard ${isFlipped ? 'flipped' : ''}`}>
        {/* Front of card */}
        <div className="flashcard-face flashcard-front">
          <div className="flashcard-content">
            <Badge className={getDifficultyColor(word?.difficulty)}>
              {word?.difficulty}
            </Badge>
            
            <h2 className="flashcard-word">
              {word?.word}
            </h2>
            
            {word?.pronunciation && (
              <div className="flashcard-pronunciation">
                <p className="pronunciation-text">
                  {word.pronunciation}
                </p>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={(e) => {
                    e.stopPropagation();
                    onPronounce();
                  }}
                  className="pronunciation-btn"
                >
                  <Volume2 className="h-4 w-4" />
                </Button>
              </div>
            )}
            
            <div className="flip-hint">
              <RotateCcw className="h-4 w-4 mr-2" />
              Click to reveal definition
            </div>
          </div>
        </div>

        {/* Back of card */}
        <div className="flashcard-face flashcard-back">
          <div className="flashcard-content">
            <h3 className="flashcard-word-back">
              {word?.word}
            </h3>
            
            <div className="definitions-container">
              {word?.definitions?.slice(0,2).map((def, index) => (
                <div key={index} className="definition-item">
                  <p className="definition-text">{def.definition}</p>
                  {def.example && (
                    <p className="example-text">
                      "{def.example}"
                    </p>
                  )}
                </div>
              ))}
            </div>
            
            <div className="flip-hint">
              How well did you know this word?
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimatedFlashcard;
