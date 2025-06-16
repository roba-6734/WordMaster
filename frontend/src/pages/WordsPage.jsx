import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api.js';
import AddWordModal from '../components/AddWordModal';
import WordDetailsModal from '../components/WordDetailsModal';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  BookOpen, 
  Search, 
  Plus, 
  Filter,
  MoreVertical,
  Calendar,
  Target,
  Volume2,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import { Link } from 'react-router-dom';

const WordsPage = () => {
  const { user } = useAuth();
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedWord, setSelectedWord] = useState(null);
  

  useEffect(() => {
    loadWords();
  }, [currentPage, searchTerm, filterDifficulty, sortBy]);

  const loadWords = async () => {
    try {
      setLoading(true);
      const response = await apiService.getWords(currentPage, 20, searchTerm);
      console.log(response)
      setWords(response.words || []);
      setTotalPages(response.total_pages || 1);
    } catch (error) {
      console.error('Failed to load words:', error);
      // For demo purposes, show sample data
      setWords(generateSampleWords());
    } finally {
      setLoading(false);
    }
  };

  const generateSampleWords = () => [
    {
      id: 1,
      word: "serendipity",
      definitions: [{ definition: "The occurrence of events by chance in a happy way" }],
      difficulty: "intermediate",
      created_at: "2024-01-15",
      next_review: "2024-01-20",
      mastery_level: 3
    },
    {
      id: 2,
      word: "ephemeral",
      definitions: [{ definition: "Lasting for a very short time" }],
      difficulty: "advanced",
      created_at: "2024-01-14",
      next_review: "2024-01-19",
      mastery_level: 2
    },
    {
      id: 3,
      word: "ubiquitous",
      definitions: [{ definition: "Present, appearing, or found everywhere" }],
      difficulty: "advanced",
      created_at: "2024-01-13",
      next_review: "2024-01-18",
      mastery_level: 4
    },
    {
      id: 4,
      word: "mellifluous",
      definitions: [{ definition: "Sweet or musical; pleasant to hear" }],
      difficulty: "advanced",
      created_at: "2024-01-12",
      next_review: "2024-01-17",
      mastery_level: 1
    },
    {
      id: 5,
      word: "perspicacious",
      definitions: [{ definition: "Having keen insight; mentally sharp" }],
      difficulty: "advanced",
      created_at: "2024-01-11",
      next_review: "2024-01-16",
      mastery_level: 2
    }
  ];

  const filteredWords = words.filter(word => {
    const matchesSearch = word.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         word.definitions?.[0]?.definition.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = filterDifficulty === 'all' || word.difficulty === filterDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMasteryColor = (level) => {
    if (level >= 4) return 'bg-green-500';
    if (level >= 3) return 'bg-yellow-500';
    if (level >= 2) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const handleWordAdded = () => {
  loadWords(); // Refresh the word list
};
const handleEditWord = (word) => {
  // You can implement edit functionality later
  console.log('Edit word:', word);
};
const handleDeleteWord = async (wordId) => {
  // Implement delete functionality
  await apiService.deleteWord(wordId);
  loadWords();
};
const handleStudyWord = (word) => {
  // Navigate to study mode with this word
  console.log('Study word:', word);
};

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" />
            Words Library
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage your vocabulary collection ({filteredWords.length} words)
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Word
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <Label htmlFor="search">Search Words</Label>
              <div className="relative mt-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search by word or definition..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Difficulty Filter */}
            <div className="w-full md:w-48">
              <Label>Difficulty</Label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-full mt-1 justify-between">
                    <Filter className="h-4 w-4 mr-2" />
                    {filterDifficulty === 'all' ? 'All Levels' : 
                     filterDifficulty.charAt(0).toUpperCase() + filterDifficulty.slice(1)}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterDifficulty('all')}>
                    All Levels
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterDifficulty('beginner')}>
                    Beginner
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterDifficulty('intermediate')}>
                    Intermediate
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterDifficulty('advanced')}>
                    Advanced
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Sort */}
            <div className="w-full md:w-48">
              <Label>Sort By</Label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-full mt-1 justify-between">
                    {sortBy === 'recent' ? 'Recently Added' :
                     sortBy === 'alphabetical' ? 'A-Z' :
                     sortBy === 'difficulty' ? 'Difficulty' : 'Due Soon'}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setSortBy('recent')}>
                    Recently Added
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy('alphabetical')}>
                    Alphabetical (A-Z)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy('difficulty')}>
                    By Difficulty
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy('due')}>
                    Due for Review
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Words Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWords.map((word) => (
          <Card key={word.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-xl font-bold text-primary">
                    {word.word}
                  </CardTitle>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={getDifficultyColor(word.difficulty)}>
                      {word.difficulty}
                    </Badge>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${getMasteryColor(word.mastery_level)}`}></div>
                      <span className="text-xs text-muted-foreground">
                        Level {word.mastery_level}
                      </span>
                    </div>
                  </div>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setSelectedWord(word)}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Volume2 className="h-4 w-4 mr-2" />
                      Pronounce
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-red-600">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            
            <CardContent>
              <p className="text-muted-foreground mb-3">
                {word.definitions?.[0]?.definition || 'No definition available'}
              </p>
              
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  Added {new Date(word.added_at).toLocaleDateString()}
                </div>
                <div className="flex items-center gap-1">
                  <Target className="h-3 w-3" />
                  Review {new Date(word.next_review).toLocaleDateString()}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredWords.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No words found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm ? 'Try adjusting your search or filters' : 'Start building your vocabulary by adding your first word'}
            </p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Word
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <Button 
            variant="outline" 
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </Button>
          <span className="flex items-center px-4 text-sm text-muted-foreground">
            Page {currentPage} of {totalPages}
          </span>
          <Button 
            variant="outline" 
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      )}
      <AddWordModal 
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onWordAdded={handleWordAdded}
        />

        {/* Word Details Modal */}
        <WordDetailsModal 
        isOpen={!!selectedWord}
        onClose={() => setSelectedWord(null)}
        word={selectedWord}
        onEdit={handleEditWord}
        onDelete={handleDeleteWord}
        onStudy={handleStudyWord}
        />
    </div>
  );
};

export default WordsPage;
