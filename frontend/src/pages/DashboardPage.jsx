import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BookOpen, 
  Brain, 
  Target, 
  TrendingUp, 
  Calendar,
  Award,
  Plus,
  Play,
  BarChart3
} from 'lucide-react';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recentWords, setRecentWords] = useState([]);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Load user statistics
        const statsData = await apiService.getStats();
        setStats(statsData);

        // Load recent words
        //const wordsData = await apiService.getWords(1, 5);
        //setRecentWords(wordsData.words || []);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const progressPercentage = stats ? Math.min((stats.total_words / 100) * 100, 100) : 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.full_name || user?.email}!</h1>
          <p className="text-muted-foreground mt-1">
            Continue your vocabulary learning journey
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/words">
              <Plus className="h-4 w-4 mr-2" />
              Add Word
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/study">
              <Play className="h-4 w-4 mr-2" />
              Study Now
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Words</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_words_added || 0}</div>
            <p className="text-xs text-muted-foreground">
              +{stats?.words_this_week || 0} this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Due Today</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.due_today || 0}</div>
            <p className="text-xs text-muted-foreground">
              Words to review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Accuracy</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.overall_accuracy ? `${Math.round(stats.overall_accuracy)}%` : '0%'}
            </div>
            <p className="text-xs text-muted-foreground">
              Overall performance
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Streak</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.current_streak || 0}</div>
            <p className="text-xs text-muted-foreground">
              Days in a row
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Progress Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Learning Progress
            </CardTitle>
            <CardDescription>
              Your vocabulary building journey
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Words Learned</span>
                <span>{stats?.total_words || 0}/100</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>
            
            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats?.mastered_words || 0}
                </div>
                <div className="text-sm text-muted-foreground">Mastered</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {stats?.learning_words || 0}
                </div>
                <div className="text-sm text-muted-foreground">Learning</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Continue your learning
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button asChild className="w-full justify-start">
              <Link to="/study">
                <Play className="h-4 w-4 mr-2" />
                Start Study Session
                {stats?.due_today > 0 && (
                  <Badge variant="secondary" className="ml-auto">
                    {stats.due_today}
                  </Badge>
                )}
              </Link>
            </Button>
            
            <Button variant="outline" asChild className="w-full justify-start">
              <Link to="/quiz">
                <Target className="h-4 w-4 mr-2" />
                Take a Quiz
              </Link>
            </Button>
            
            <Button variant="outline" asChild className="w-full justify-start">
              <Link to="/words">
                <BookOpen className="h-4 w-4 mr-2" />
                Browse Words
              </Link>
            </Button>
            
            <Button variant="outline" asChild className="w-full justify-start">
              <Link to="/progress">
                <BarChart3 className="h-4 w-4 mr-2" />
                View Progress
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Words */}
      {recentWords.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Words</CardTitle>
            <CardDescription>
              Words you've added recently
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentWords.map((word) => (
                <div
                  key={word.id}
                  className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="font-medium">{word.word}</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {word.definitions?.[0]?.definition || 'No definition available'}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <Badge variant="outline" className="text-xs">
                      {word.difficulty || 'New'}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(word.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button variant="outline" asChild>
                <Link to="/words">View All Words</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardPage;
