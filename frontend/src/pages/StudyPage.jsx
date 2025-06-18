import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import AnimatedFlashcard from '../components/AnimatedFlashcard';
import { 
  Brain, 
  CheckCircle, 
  XCircle,
  Clock,
  Target,
  TrendingUp,
  Home,
  RefreshCw,
  Award,
  BookOpen
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const StudyPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Session state
  const [studyWords, setStudyWords] = useState([]);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [showDefinition, setShowDefinition] = useState(false);
  const [sessionStats, setSessionStats] = useState({
    correct: 0,
    incorrect: 0,
    total: 0
  });
  const [sessionComplete, setSessionComplete] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadStudySession();
  }, []);

  const loadStudySession = async () => {
    try {
      setLoading(true);
      const response = await apiService.getWords();
      
      if (response.words && response.words.length > 0) {
        
        setStudyWords(response.words);
        setSessionStats(prev => ({ ...prev, total: response.words.length }));
      } else {
        // Generate sample study words for demo
        setStudyWords(generateSampleStudyWords());
        setSessionStats(prev => ({ ...prev, total: 5 }));
      }
    } catch (error) {
      console.error('Failed to load study session:', error);
      setStudyWords(generateSampleStudyWords());
      setSessionStats(prev => ({ ...prev, total: 5 }));
    } finally {
      setLoading(false);
    }
  };

  const generateSampleStudyWords = () => [
    {
      id: 1,
      word: "serendipity",
      definitions: [{ 
        definition: "The occurrence of events by chance in a happy way",
        example: "It was pure serendipity that led me to find my dream job while browsing social media."
      }],
      difficulty: "intermediate",
      mastery_level: 2,
      pronunciation: "/ˌserənˈdipədē/"
    },
    {
      id: 2,
      word: "ephemeral",
      definitions: [{ 
        definition: "Lasting for a very short time",
        example: "The beauty of cherry blossoms is ephemeral, lasting only a few weeks each spring."
      }],
      difficulty: "advanced",
      mastery_level: 1,
      pronunciation: "/əˈfem(ə)rəl/"
    },
    {
      id: 3,
      word: "ubiquitous",
      definitions: [{ 
        definition: "Present, appearing, or found everywhere",
        example: "Smartphones have become ubiquitous in modern society."
      }],
      difficulty: "advanced",
      mastery_level: 3,
      pronunciation: "/yo͞oˈbikwədəs/"
    },
    {
      id: 4,
      word: "mellifluous",
      definitions: [{ 
        definition: "Sweet or musical; pleasant to hear",
        example: "The singer's mellifluous voice captivated the entire audience."
      }],
      difficulty: "advanced",
      mastery_level: 1,
      pronunciation: "/məˈliflo͞oəs/"
    },
    {
      id: 5,
      word: "perspicacious",
      definitions: [{ 
        definition: "Having keen insight; mentally sharp",
        example: "Her perspicacious analysis of the market trends impressed the board of directors."
      }],
      difficulty: "advanced",
      mastery_level: 2,
      pronunciation: "/ˌpərspəˈkāSHəs/"
    }
  ];

  const currentWord = studyWords[currentWordIndex];
  const progressPercentage = studyWords.length > 0 ? ((currentWordIndex + 1) / studyWords.length) * 100 : 0;

  const handleFlipCard = () => {
    setShowDefinition(!showDefinition);
  };

  const playPronunciation = () => {
    if (currentWord?.word) {
      const utterance = new SpeechSynthesisUtterance(currentWord.word);
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const handleDifficultyResponse = async (difficulty) => {
    if (!currentWord) return;

    setSubmitting(true);
    
    try {
      // Update word progress based on difficulty response
      await apiService.updateWordProgress(currentWord.id, difficulty);
      
      // Update session stats
      const isCorrect = difficulty === 'easy' || difficulty === 'medium';
      setSessionStats(prev => ({
        ...prev,
        correct: isCorrect ? prev.correct + 1 : prev.correct,
        incorrect: !isCorrect ? prev.incorrect + 1 : prev.incorrect
      }));

      // Move to next word or complete session
      if (currentWordIndex < studyWords.length - 1) {
        setCurrentWordIndex(currentWordIndex + 1);
        setShowDefinition(false);
      } else {
        setSessionComplete(true);
      }
    } catch (error) {
      console.error('Failed to update word progress:', error);
      // Continue anyway for demo
      const isCorrect = difficulty === 'easy' || difficulty === 'medium';
      setSessionStats(prev => ({
        ...prev,
        correct: isCorrect ? prev.correct + 1 : prev.correct,
        incorrect: !isCorrect ? prev.incorrect + 1 : prev.incorrect
      }));

      if (currentWordIndex < studyWords.length - 1) {
        setCurrentWordIndex(currentWordIndex + 1);
        setShowDefinition(false);
      } else {
        setSessionComplete(true);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const startNewSession = () => {
    setCurrentWordIndex(0);
    setShowDefinition(false);
    setSessionStats({ correct: 0, incorrect: 0, total: studyWords.length });
    setSessionComplete(false);
    loadStudySession();
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your study session...</p>
          </div>
        </div>
      </div>
    );
  }

  if (studyWords.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-12 text-center">
            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">No Words to Study</h2>
            <p className="text-muted-foreground mb-6">
              You don't have any words due for review right now. Add some words to your library or check back later!
            </p>
            <div className="flex gap-2 justify-center">
              <Button asChild>
                <Link to="/words">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Browse Words
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/dashboard">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (sessionComplete) {
    const accuracy = sessionStats.total > 0 ? Math.round((sessionStats.correct / sessionStats.total) * 100) : 0;
    const performance = accuracy >= 80 ? 'excellent' : accuracy >= 60 ? 'good' : 'needs-improvement';
    
    return (
      <div className="container mx-auto p-6">
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              {performance === 'excellent' ? (
                <Award className="h-16 w-16 text-yellow-500" />
              ) : performance === 'good' ? (
                <CheckCircle className="h-16 w-16 text-green-500" />
              ) : (
                <Target className="h-16 w-16 text-blue-500" />
              )}
            </div>
            <CardTitle className="text-2xl">
              {performance === 'excellent' ? 'Excellent Work!' :
               performance === 'good' ? 'Good Job!' : 'Keep Practicing!'}
            </CardTitle>
            <CardDescription>
              You've completed your study session
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Session Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-muted/50 rounded-lg">
                <div className="text-2xl font-bold text-primary">{sessionStats.total}</div>
                <div className="text-sm text-muted-foreground">Words Studied</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{sessionStats.correct}</div>
                <div className="text-sm text-muted-foreground">Correct</div>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{sessionStats.incorrect}</div>
                <div className="text-sm text-muted-foreground">Needs Review</div>
              </div>
            </div>

            {/* Accuracy */}
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Session Accuracy</span>
                <span className="font-medium">{accuracy}%</span>
              </div>
              <Progress value={accuracy} className="h-3" />
            </div>

            {/* Performance Message */}
            <Alert>
              <TrendingUp className="h-4 w-4" />
              <AlertDescription>
                {performance === 'excellent' && 
                  "Outstanding! You're mastering these words quickly. Keep up the great work!"
                }
                {performance === 'good' && 
                  "Good progress! A few more reviews and you'll have these words mastered."
                }
                {performance === 'needs-improvement' && 
                  "Don't worry, learning takes time. Try reviewing these words again soon."
                }
              </AlertDescription>
            </Alert>

            {/* Action Buttons */}
            <div className="flex gap-2 justify-center">
              <Button onClick={startNewSession}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Study More
              </Button>
              <Button variant="outline" asChild>
                <Link to="/dashboard">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/progress">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  View Progress
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-primary" />
            Study Session
          </h1>
          <p className="text-muted-foreground mt-1">
            Review your vocabulary with spaced repetition
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/dashboard">
            <Home className="h-4 w-4 mr-2" />
            Dashboard
          </Link>
        </Button>
      </div>

      {/* Progress Bar */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Progress</span>
            <span className="text-sm text-muted-foreground">
              {currentWordIndex + 1} of {studyWords.length}
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </CardContent>
      </Card>

      {/* Animated Flashcard */}
      <AnimatedFlashcard 
        word={currentWord}
        onFlip={handleFlipCard}
        isFlipped={showDefinition}
        onPronounce={playPronunciation}
      />

      {/* Action Buttons */}
      <div className="flex justify-center gap-4 mb-6">
        {showDefinition && (
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              className="text-red-600 border-red-200 hover:bg-red-50"
              onClick={() => handleDifficultyResponse('hard')}
              disabled={submitting}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Hard
            </Button>
            <Button 
              variant="outline"
              className="text-yellow-600 border-yellow-200 hover:bg-yellow-50"
              onClick={() => handleDifficultyResponse('medium')}
              disabled={submitting}
            >
              <Clock className="h-4 w-4 mr-2" />
              Medium
            </Button>
            <Button 
              className="text-green-600 bg-green-50 border-green-200 hover:bg-green-100"
              onClick={() => handleDifficultyResponse('easy')}
              disabled={submitting}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Easy
            </Button>
          </div>
        )}
      </div>

      {/* Session Stats */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <div className="font-medium text-green-600">{sessionStats.correct}</div>
              <div className="text-muted-foreground">Correct</div>
            </div>
            <div>
              <div className="font-medium text-red-600">{sessionStats.incorrect}</div>
              <div className="text-muted-foreground">Incorrect</div>
            </div>
            <div>
              <div className="font-medium text-primary">
                {sessionStats.total - sessionStats.correct - sessionStats.incorrect}
              </div>
              <div className="text-muted-foreground">Remaining</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StudyPage;
