export interface ProductLink {
    id: string;
    title: string;
    url: string;   // full amazon link (https://...)
    image: string; // full image link
    price?: string;
    rating?: number;
}

export interface RecommendResponse {
    text: string;
    links: ProductLink[];
}
