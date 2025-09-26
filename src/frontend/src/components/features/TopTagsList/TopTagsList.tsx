/**
 * Top Tags List Component
 * Shows top tags with their related sub-tags in a clean, structured layout
 */

import { useState, useEffect } from 'react';
import { Hash, TrendingUp } from 'lucide-react';
import { apiClient, type Tag as TagType } from '../../../api/client';

interface TopTagsListProps {
  className?: string;
  maxTopTags?: number;
  maxSubTags?: number;
}

interface TagActivity {
  name: string;
  time: string;
  usage_count: number;
  keywords: string[];
}

export const TopTagsList: React.FC<TopTagsListProps> = ({ 
  className,
  maxTopTags = 5,
  maxSubTags = 5
}) => {
  const [topActivities, setTopActivities] = useState<TagActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTagData();
  }, []);

  const loadTagData = async () => {
    setLoading(true);
    try {
      // Use the new API endpoint for real tag relationships
      const relationshipsRes = await apiClient.getTopTagsWithRelationships(
        maxTopTags,
        maxSubTags
      );
      
      if (relationshipsRes.error) throw new Error(relationshipsRes.error);
      
      setTopActivities(relationshipsRes.data || []);
    } catch (error) {
      console.error('Error loading tag data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`card-artistic rounded-3xl p-8 ${className}`}>
        <div className="mb-6">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
            Top 5 Activities
          </h2>
          <p className="text-muted-foreground mt-2">Your most engaging pursuits</p>
        </div>
        <div className="flex items-center justify-center p-8 text-muted-foreground">
          Loading tag data...
        </div>
      </div>
    );
  }

  if (topActivities.length === 0) {
    return (
      <div className={`card-artistic rounded-3xl p-8 ${className}`}>
        <div className="mb-6">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
            Top 5 Activities
          </h2>
          <p className="text-muted-foreground mt-2">Your most engaging pursuits</p>
        </div>
        <div className="text-center p-8 text-muted-foreground">
          <p>No tag data available yet.</p>
          <p>Start tracking activities to see your top pursuits!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`card-artistic rounded-3xl p-8 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
          Top 5 Activities
        </h2>
        <p className="text-muted-foreground mt-2">Your most engaging pursuits</p>
      </div>
      <div className="space-y-6">
        {topActivities.map((activity, index) => (
          <div
            key={index}
            className="space-y-3 p-4 rounded-xl bg-gradient-to-r from-muted/30 to-muted/10 hover:from-muted/50 hover:to-muted/20 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-sm">
                  {index + 1}
                </div>
                <h4 className="font-semibold text-foreground">{activity.name}</h4>
              </div>
              <span className="text-sm font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                {activity.time}
              </span>
            </div>
            <div className="flex flex-wrap gap-2 ml-11">
              {activity.keywords.map((keyword, keyIndex) => (
                <span
                  key={keyIndex}
                  className="text-xs bg-gradient-to-r from-secondary/20 to-accent/20 hover:from-secondary/30 hover:to-accent/30 border-0 transition-all duration-200 px-2 py-1 rounded-md"
                >
                  {keyword}
                </span>
              ))}
            </div>
            {index < topActivities.length - 1 && (
              <div className="border-b border-gradient-to-r from-transparent via-border to-transparent ml-11" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};