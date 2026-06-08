export interface Poem {
  id: string;
  title: string;
  author: string;
  dynasty: string;
  content: string[];
  score?: number;
}

export interface SearchResponse {
  results: Poem[];
  query: string;
}
