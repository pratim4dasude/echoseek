"use client";

import { ProductLink } from "@/app/types";

export default function ProductCard({ item }: { item: ProductLink }) {
    return (
        <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block rounded-2xl border border-zinc-200 bg-white shadow-sm hover:shadow-md transition overflow-hidden"
        >
            {/* Product image */}
            <div className="aspect-[4/3] bg-zinc-100 overflow-hidden">
                <img
                    src={item.image}
                    alt={item.title}
                    className="h-full w-full object-cover group-hover:scale-105 transition-transform"
                    loading="lazy"
                />
            </div>

            {/* Product info */}
            <div className="p-3 text-left">
                <h3 className="text-sm font-medium text-zinc-900 line-clamp-2 group-hover:text-orange-600 transition-colors">
                    {item.title}
                </h3>

                {item.price && (
                    <p className="mt-1 text-sm font-semibold text-green-700">{item.price}</p>
                )}

                {item.rating && (
                    <p className="mt-1 text-xs text-yellow-700">
                        {"★".repeat(Math.round(item.rating))}{" "}
                        <span className="text-zinc-500">{item.rating.toFixed(1)}</span>
                    </p>
                )}
            </div>
        </a>
    );
}
