"""
Test script for Gemini-powered feature engineering.
Demonstrates AI-driven feature generation and analysis.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from backend.models.gemini_feature_engineer import GeminiFeatureEngineer, engineer_features_with_ai
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_feature_engineering():
    """Test AI-powered feature engineering."""
    
    print_section("Gemini Feature Engineering Test")
    
    # Initialize feature engineer
    try:
        engineer = GeminiFeatureEngineer()
        print("✅ GeminiFeatureEngineer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nMake sure GEMINI_API_KEY is set in your .env file")
        return
    
    # Create sample data with minimal features
    print_section("Sample Data (Minimal Features)")
    
    sample_data = pd.DataFrame([
        {
            'person_age': 30,
            'person_income': 50000,
            'loan_amnt': 15000,
            'loan_int_rate': 12.5
        },
        {
            'person_age': 25,
            'person_income': 35000,
            'loan_amnt': 25000,
            'loan_int_rate': 18.5
        },
        {
            'person_age': 45,
            'person_income': 75000,
            'loan_amnt': 20000,
            'loan_int_rate': 8.5
        }
    ])
    
    print("\n📋 Original Data:")
    print(sample_data.to_string(index=False))
    print(f"\nOriginal features: {list(sample_data.columns)}")
    print(f"Total rows: {len(sample_data)}")
    
    # Analyze data
    print_section("AI Analysis")
    
    try:
        print("\n🔍 Analyzing data with Gemini AI...")
        analysis = engineer.analyze_data(sample_data)
        
        print(f"\n📊 Data Quality Score: {analysis['data_quality']['completeness_score']}/100")
        
        if analysis['data_quality']['issues']:
            print(f"\n⚠️  Issues Found:")
            for issue in analysis['data_quality']['issues'][:3]:
                print(f"  • {issue}")
        
        if analysis['data_quality']['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['data_quality']['recommendations'][:3]:
                print(f"  • {rec}")
        
        print(f"\n🎯 Recommended Features to Generate:")
        for feature in analysis.get('recommended_features', [])[:5]:
            print(f"\n  Feature: {feature['name']}")
            print(f"  Description: {feature['description']}")
            print(f"  Formula: {feature['formula']}")
            print(f"  Rationale: {feature['rationale']}")
        
        if analysis.get('missing_critical_features'):
            print(f"\n🔴 Missing Critical Features:")
            for missing in analysis['missing_critical_features'][:3]:
                print(f"  • {missing['name']} (Importance: {missing['importance']})")
                print(f"    Strategy: {missing['imputation_strategy']}")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate features
    print_section("Feature Generation")
    
    try:
        print("\n⚙️  Generating features...")
        engineered_data = engineer.generate_features(sample_data, analysis)
        
        # Get new features
        new_features = list(set(engineered_data.columns) - set(sample_data.columns))
        
        print(f"\n✅ Feature engineering complete!")
        print(f"\nOriginal features: {len(sample_data.columns)}")
        print(f"New features generated: {len(new_features)}")
        print(f"Total features: {len(engineered_data.columns)}")
        
        if new_features:
            print(f"\n🆕 New Features:")
            for feature in new_features[:10]:
                print(f"  • {feature}")
        
        print(f"\n📋 Engineered Data Sample:")
        print(engineered_data.head(3).to_string(index=False))
        
        # Show feature statistics
        print(f"\n📈 Feature Statistics:")
        for feature in new_features[:5]:
            if feature in engineered_data.columns:
                col = engineered_data[feature]
                if pd.api.types.is_numeric_dtype(col):
                    print(f"\n  {feature}:")
                    print(f"    Min: {col.min():.2f}")
                    print(f"    Max: {col.max():.2f}")
                    print(f"    Mean: {col.mean():.2f}")
        
    except Exception as e:
        print(f"\n❌ Feature generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test convenience function
    print_section("Convenience Function Test")
    
    try:
        print("\n🚀 Testing engineer_features_with_ai()...")
        result = engineer_features_with_ai(sample_data)
        
        print(f"\n✅ Success!")
        print(f"  Original features: {len(result['original_data'].columns)}")
        print(f"  Engineered features: {result['total_features']}")
        print(f"  New features: {len(result['new_features'])}")
        
        if result['new_features']:
            print(f"\n  Generated:")
            for feature in result['new_features'][:5]:
                print(f"    • {feature}")
        
    except Exception as e:
        print(f"\n❌ Convenience function failed: {e}")
    
    # Save results
    print_section("Saving Results")
    
    try:
        # Save engineered data
        engineered_data.to_csv('engineered_features_sample.csv', index=False)
        print("\n✅ Saved: engineered_features_sample.csv")
        
        # Save analysis
        with open('feature_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print("✅ Saved: feature_analysis.json")
        
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    print_section("Test Complete")
    
    print("\n✅ Feature engineering test completed successfully!")
    print("\nKey Takeaways:")
    print("  • AI analyzed your data and identified missing features")
    print("  • Generated domain-specific credit risk features")
    print("  • Created derived features from existing data")
    print("  • Provided recommendations for data quality improvement")
    print("\nNext steps:")
    print("  1. Review feature_analysis.json for detailed insights")
    print("  2. Check engineered_features_sample.csv for results")
    print("  3. Use POST /analyze_features endpoint in production")
    print("  4. Use POST /engineer_features endpoint for batch processing")


if __name__ == "__main__":
    test_feature_engineering()
