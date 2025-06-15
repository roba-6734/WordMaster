import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Plus, 
  X, 
  Search, 
  Loader2, 
  CheckCircle,
  AlertCircle,
  Volume2
} from 'lucide-react';
import apiService from '../services/api';

const AddWordModal = ({ isOpen, onClose, onWordAdded }) => {
  const [formData, setFormData] = useState({
    word: '',
    difficulty: 'intermediate',
    definitions: [{ definition: '', example: '' }],
    pronunciation: '',
    partOfSpeech: ''
  });
  const [loading, setLoading] = useState(false);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const resetForm = () => {
    setFormData({
      word: '',
      difficulty: 'intermediate',
      definitions: [{ definition: '', example: '' }],
      pronunciation: '',
      partOfSpeech: ''
    });
    setError('');
    setSuccess(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDefinitionChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      definitions: prev.definitions.map((def, i) => 
        i === index ? { ...def, [field]: value } : def
      )
    }));
  };

  const addDefinition = () => {
    setFormData(prev => ({
      ...prev,
      definitions: [...prev.definitions, { definition: '', example: '' }]
    }));
  };

  const removeDefinition = (index) => {
    if (formData.definitions.length > 1) {
      setFormData(prev => ({
        ...prev,
        definitions: prev.definitions.filter((_, i) => i !== index)
      }));
    }
  };

  const lookupWord = async () => {
    if (!formData.word.trim()) {
      setError('Please enter a word to look up');
      return;
    }

    setLookupLoading(true);
    setError('');

    try {
      const result = await apiService.lookupWord(formData.word);
      
      if (result.definitions && result.definitions.length > 0) {
        setFormData(prev => ({
          ...prev,
          definitions: result.definitions.map(def => ({
            definition: def.definition || '',
            example: def.example || ''
          })),
          pronunciation: result.pronunciation || '',
          partOfSpeech: result.part_of_speech || ''
        }));
      } else {
        setError('No definitions found for this word');
      }
    } catch (error) {
      console.error('Lookup failed:', error);
      setError('Failed to look up word. You can add it manually.');
    } finally {
      setLookupLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.word.trim()) {
      setError('Word is required');
      return;
    }

    if (!formData.definitions[0].definition.trim()) {
      setError('At least one definition is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await apiService.addWord(formData);
      setSuccess(true);
      
      // Show success for 1.5 seconds, then close
      setTimeout(() => {
        handleClose();
        onWordAdded?.();
      }, 1500);
    } catch (error) {
      setError(error.message || 'Failed to add word');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800 hover:bg-green-200';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
      case 'advanced': return 'bg-red-100 text-red-800 hover:bg-red-200';
      default: return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
    }
  };

  if (success) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-md">
          <div className="flex flex-col items-center justify-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Word Added Successfully!</h3>
            <p className="text-muted-foreground text-center">
              "{formData.word}" has been added to your vocabulary.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add New Word
          </DialogTitle>
          <DialogDescription>
            Add a new word to your vocabulary. You can look it up automatically or enter details manually.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Word Input with Lookup */}
          <div className="space-y-2">
            <Label htmlFor="word">Word *</Label>
            <div className="flex gap-2">
              <Input
                id="word"
                value={formData.word}
                onChange={(e) => handleInputChange('word', e.target.value)}
                placeholder="Enter the word..."
                className="flex-1"
              />
              <Button 
                type="button" 
                variant="outline" 
                onClick={lookupWord}
                disabled={lookupLoading || !formData.word.trim()}
              >
                {lookupLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Difficulty and Part of Speech */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Difficulty Level</Label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-full justify-between">
                    <Badge className={getDifficultyColor(formData.difficulty)}>
                      {formData.difficulty.charAt(0).toUpperCase() + formData.difficulty.slice(1)}
                    </Badge>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => handleInputChange('difficulty', 'beginner')}>
                    <Badge className="bg-green-100 text-green-800">Beginner</Badge>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleInputChange('difficulty', 'intermediate')}>
                    <Badge className="bg-yellow-100 text-yellow-800">Intermediate</Badge>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleInputChange('difficulty', 'advanced')}>
                    <Badge className="bg-red-100 text-red-800">Advanced</Badge>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="space-y-2">
              <Label htmlFor="partOfSpeech">Part of Speech</Label>
              <Input
                id="partOfSpeech"
                value={formData.partOfSpeech}
                onChange={(e) => handleInputChange('partOfSpeech', e.target.value)}
                placeholder="noun, verb, adjective..."
              />
            </div>
          </div>

          {/* Pronunciation */}
          <div className="space-y-2">
            <Label htmlFor="pronunciation">Pronunciation</Label>
            <div className="flex gap-2">
              <Input
                id="pronunciation"
                value={formData.pronunciation}
                onChange={(e) => handleInputChange('pronunciation', e.target.value)}
                placeholder="/prəˌnʌnsiˈeɪʃən/"
                className="flex-1"
              />
              <Button type="button" variant="outline" size="icon">
                <Volume2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Definitions */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Definitions *</Label>
              <Button type="button" variant="outline" size="sm" onClick={addDefinition}>
                <Plus className="h-3 w-3 mr-1" />
                Add Definition
              </Button>
            </div>

            {formData.definitions.map((def, index) => (
              <div key={index} className="space-y-3 p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">Definition {index + 1}</Label>
                  {formData.definitions.length > 1 && (
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm"
                      onClick={() => removeDefinition(index)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Input
                    value={def.definition}
                    onChange={(e) => handleDefinitionChange(index, 'definition', e.target.value)}
                    placeholder="Enter definition..."
                  />
                  <Input
                    value={def.example}
                    onChange={(e) => handleDefinitionChange(index, 'example', e.target.value)}
                    placeholder="Example sentence (optional)..."
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Adding Word...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Word
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddWordModal;
