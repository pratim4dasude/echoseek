export interface ProductLink {
    id: string;
    title: string;
    url: string;   
    image: string; 
    price?: string;
    rating?: number;
}

export interface RecommendResponse {
    text: string;
    links: ProductLink[];
}

export type LLMResponse = {
    text: string;
    links?: ProductLink[];
} | Record<string, unknown>; 