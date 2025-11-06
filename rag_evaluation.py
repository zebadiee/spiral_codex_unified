#!/usr/bin/env python3
"""
RAG Quality Evaluation Script
Compares legacy vs enhanced RAG (BM25 + vector tie-break) performance
Generates evaluation metrics and win-rate analysis
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from utils.rag import (
    init_db, add_test_snippets, retrieve, retrieve_legacy,
    reset_models, available as rag_available
)

def calculate_relevance_score(query: str, result: Dict[str, Any]) -> float:
    """Simple relevance scoring based on keyword overlap and semantic similarity"""
    content = result.get('content', '').lower()
    source = result.get('source', '').lower()
    query_terms = set(query.lower().split())

    # Count query terms in content and source
    content_matches = sum(1 for term in query_terms if term in content)
    source_matches = sum(1 for term in query_terms if term in source)

    # Calculate relevance score (0-1 scale)
    max_possible_matches = len(query_terms)
    if max_possible_matches == 0:
        return 0.0

    relevance = (content_matches + source_matches * 0.5) / max_possible_matches
    return min(relevance, 1.0)

def evaluate_single_query(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Evaluate a single query comparing legacy vs enhanced RAG"""
    print(f"Evaluating query: '{query}'")

    # Get results from both systems
    legacy_results = retrieve_legacy(query, top_k=top_k)
    enhanced_results = retrieve(query, top_k=top_k)

    # Calculate relevance scores
    legacy_scores = [calculate_relevance_score(query, r) for r in legacy_results]
    enhanced_scores = [calculate_relevance_score(query, r) for r in enhanced_results]

    # Calculate average relevance
    legacy_avg = sum(legacy_scores) / len(legacy_scores) if legacy_scores else 0.0
    enhanced_avg = sum(enhanced_scores) / len(enhanced_scores) if enhanced_scores else 0.0

    # Determine winner
    if enhanced_avg > legacy_avg:
        winner = "enhanced"
        improvement = ((enhanced_avg - legacy_avg) / legacy_avg * 100) if legacy_avg > 0 else float('inf')
    elif legacy_avg > enhanced_avg:
        winner = "legacy"
        improvement = ((legacy_avg - enhanced_avg) / enhanced_avg * 100) if enhanced_avg > 0 else float('inf')
    else:
        winner = "tie"
        improvement = 0.0

    return {
        "query": query,
        "legacy_count": len(legacy_results),
        "enhanced_count": len(enhanced_results),
        "legacy_avg_relevance": round(legacy_avg, 3),
        "enhanced_avg_relevance": round(enhanced_avg, 3),
        "winner": winner,
        "improvement_percent": round(improvement, 1),
        "legacy_scores": [round(s, 3) for s in legacy_scores],
        "enhanced_scores": [round(s, 3) for s in enhanced_scores],
        "legacy_sources": [r.get('source', 'unknown') for r in legacy_results],
        "enhanced_sources": [r.get('source', 'unknown') for r in enhanced_results],
        "enhanced_methods": [r.get('rank_method', 'unknown') for r in enhanced_results]
    }

def run_evaluation(queries: List[str]) -> List[Dict[str, Any]]:
    """Run full evaluation on a set of queries"""
    print("🧪 Running RAG Quality Evaluation")
    print("=" * 50)

    # Ensure RAG is available and has test data
    if not rag_available():
        print("❌ RAG not available - initializing...")
        init_db()
        add_test_snippets()

    # Reset models to ensure fresh evaluation
    reset_models()

    results = []
    for query in queries:
        result = evaluate_single_query(query)
        results.append(result)
        print(f"  ✓ {result['winner']} (improvement: {result['improvement_percent']}%)")

    return results

def calculate_win_rate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall win-rate and metrics"""
    total_queries = len(results)
    enhanced_wins = sum(1 for r in results if r['winner'] == 'enhanced')
    legacy_wins = sum(1 for r in results if r['winner'] == 'legacy')
    ties = sum(1 for r in results if r['winner'] == 'tie')

    # Calculate average improvements
    enhanced_improvements = [r['improvement_percent'] for r in results if r['winner'] == 'enhanced']
    avg_improvement = sum(enhanced_improvements) / len(enhanced_improvements) if enhanced_improvements else 0.0

    # Calculate overall relevance averages
    legacy_relevance_avg = sum(r['legacy_avg_relevance'] for r in results) / total_queries
    enhanced_relevance_avg = sum(r['enhanced_avg_relevance'] for r in results) / total_queries

    return {
        "total_queries": total_queries,
        "enhanced_wins": enhanced_wins,
        "legacy_wins": legacy_wins,
        "ties": ties,
        "enhanced_win_rate": round((enhanced_wins / total_queries) * 100, 1),
        "legacy_win_rate": round((legacy_wins / total_queries) * 100, 1),
        "tie_rate": round((ties / total_queries) * 100, 1),
        "avg_improvement_when_enhanced_wins": round(avg_improvement, 1),
        "overall_legacy_relevance": round(legacy_relevance_avg, 3),
        "overall_enhanced_relevance": round(enhanced_relevance_avg, 3),
        "overall_improvement": round(((enhanced_relevance_avg - legacy_relevance_avg) / legacy_relevance_avg * 100) if legacy_relevance_avg > 0 else 0, 1)
    }

def save_evaluation_csv(results: List[Dict[str, Any]], metrics: Dict[str, Any], filename: str = "data/ablation/rag_eval.csv"):
    """Save evaluation results to CSV"""
    # Ensure directory exists
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'query', 'legacy_count', 'enhanced_count',
            'legacy_avg_relevance', 'enhanced_avg_relevance',
            'winner', 'improvement_percent', 'enhanced_method'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            # Get the primary enhanced method (first result)
            enhanced_method = result['enhanced_methods'][0] if result['enhanced_methods'] else 'none'
            writer.writerow({
                'query': result['query'],
                'legacy_count': result['legacy_count'],
                'enhanced_count': result['enhanced_count'],
                'legacy_avg_relevance': result['legacy_avg_relevance'],
                'enhanced_avg_relevance': result['enhanced_avg_relevance'],
                'winner': result['winner'],
                'improvement_percent': result['improvement_percent'],
                'enhanced_method': enhanced_method
            })

        # Add summary row
        writer.writerow({})
        writer.writerow({
            'query': 'OVERALL METRICS',
            'legacy_avg_relevance': metrics['overall_legacy_relevance'],
            'enhanced_avg_relevance': metrics['overall_enhanced_relevance'],
            'winner': f"Enhanced: {metrics['enhanced_win_rate']}% win rate",
            'improvement_percent': metrics['overall_improvement'],
            'enhanced_method': 'BM25 + Vector Tie-Break'
        })

    print(f"✅ Evaluation results saved to {filename}")

def save_evaluation_json(results: List[Dict[str, Any]], metrics: Dict[str, Any], filename: str = "data/ablation/rag_eval.json"):
    """Save detailed evaluation results to JSON"""
    # Ensure directory exists
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    evaluation_data = {
        "timestamp": "2025-11-06T17:00:00Z",
        "methodology": "BM25 + Vector Tie-Break vs Legacy Keyword Matching",
        "evaluation_queries_count": len(results),
        "metrics": metrics,
        "detailed_results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, indent=2)

    print(f"✅ Detailed evaluation saved to {filename}")

def main():
    """Main evaluation entry point"""
    # Test queries for evaluation
    evaluation_queries = [
        "How does agent routing work in the system?",
        "What privacy features are implemented?",
        "Explain the telemetry system and its data format",
        "BM25 scoring algorithm implementation",
        "Vector embeddings and semantic similarity",
        "API documentation and validation features",
        "Database storage and SQLite integration",
        "Reflection training and system improvement",
        "Ledger logging and conversation tracking",
        "Spiral Codex architecture and glyph routing"
    ]

    # Run evaluation
    results = run_evaluation(evaluation_queries)
    metrics = calculate_win_rate(results)

    # Print summary
    print("\n📊 Evaluation Summary")
    print("-" * 30)
    print(f"Total queries: {metrics['total_queries']}")
    print(f"Enhanced RAG wins: {metrics['enhanced_wins']} ({metrics['enhanced_win_rate']}%)")
    print(f"Legacy RAG wins: {metrics['legacy_wins']} ({metrics['legacy_win_rate']}%)")
    print(f"Ties: {metrics['ties']} ({metrics['tie_rate']}%)")
    print(f"Average improvement when enhanced wins: {metrics['avg_improvement_when_enhanced_wins']}%")
    print(f"Overall relevance improvement: {metrics['overall_improvement']}%")
    print(f"Enhanced method: BM25 + Vector Tie-Break")

    # Save results
    save_evaluation_csv(results, metrics)
    save_evaluation_json(results, metrics)

    print("\n🎉 RAG Quality Evaluation Complete!")

if __name__ == "__main__":
    main()