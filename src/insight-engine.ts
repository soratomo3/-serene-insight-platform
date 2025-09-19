/**
 * Serena洞察発見エンジン
 * データから自動的に洞察を抽出し、アクション可能な推奨事項を生成
 */

interface DataPoint {
  [key: string]: number | string | Date;
}

interface Insight {
  type: string;
  insight: string;
  confidence: number;
  actionable: string;
  priority: 'high' | 'medium' | 'low';
  data?: any;
}

interface TimeSeriesData {
  date: Date;
  value: number;
}

interface CustomerData {
  customerId: string;
  recency: number;
  frequency: number;
  monetary: number;
}

class SerenaInsightEngine {
  private insights: Insight[] = [];
  
  constructor() {
    console.log('🔍 Serena洞察エンジン初期化完了');
  }

  /**
   * 季節性パターン分析
   */
  analyzeSeasonality(data: TimeSeriesData[]): Insight[] {
    const insights: Insight[] = [];
    
    // 月別集計
    const monthlyData = new Map<number, number[]>();
    data.forEach(item => {
      const month = item.date.getMonth() + 1;
      if (!monthlyData.has(month)) {
        monthlyData.set(month, []);
      }
      monthlyData.get(month)!.push(item.value);
    });
    
    // 月別平均計算
    const monthlyAvg = new Map<number, number>();
    monthlyData.forEach((values, month) => {
      const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
      monthlyAvg.set(month, avg);
    });
    
    // ピーク・ボトム月の特定
    const avgValues = Array.from(monthlyAvg.values());
    const maxAvg = Math.max(...avgValues);
    const minAvg = Math.min(...avgValues);
    const overallAvg = avgValues.reduce((sum, val) => sum + val, 0) / avgValues.length;
    
    const peakMonth = Array.from(monthlyAvg.entries())
      .find(([_, avg]) => avg === maxAvg)?.[0] || 1;
    const lowMonth = Array.from(monthlyAvg.entries())
      .find(([_, avg]) => avg === minAvg)?.[0] || 1;
    
    const seasonalVariation = ((maxAvg - minAvg) / overallAvg * 100);
    
    insights.push({
      type: '季節性洞察',
      insight: `売上は${peakMonth}月にピーク（平均${maxAvg.toFixed(0)}）、${lowMonth}月が最低（平均${minAvg.toFixed(0)}）。季節変動は${seasonalVariation.toFixed(1)}%`,
      confidence: 85,
      actionable: `${peakMonth}月前の在庫増強と${lowMonth}月の販促強化を推奨`,
      priority: seasonalVariation > 30 ? 'high' : 'medium',
      data: { peakMonth, lowMonth, variation: seasonalVariation }
    });
    
    return insights;
  }

  /**
   * トレンド分析
   */
  analyzeTrend(data: TimeSeriesData[]): Insight[] {
    const insights: Insight[] = [];
    
    if (data.length < 10) return insights;
    
    // 線形回帰による成長率計算
    const n = data.length;
    const sortedData = data.sort((a, b) => a.date.getTime() - b.date.getTime());
    
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
    
    sortedData.forEach((item, index) => {
      sumX += index;
      sumY += item.value;
      sumXY += index * item.value;
      sumX2 += index * index;
    });
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // 成長率の評価
    const firstValue = sortedData[0].value;
    const lastValue = sortedData[n - 1].value;
    const totalGrowthRate = ((lastValue - firstValue) / firstValue * 100);
    
    const trendType = slope > 0 ? '成長' : '減少';
    const priority: 'high' | 'medium' | 'low' = 
      Math.abs(totalGrowthRate) > 20 ? 'high' :
      Math.abs(totalGrowthRate) > 10 ? 'medium' : 'low';
    
    insights.push({
      type: 'トレンド洞察',
      insight: `データは${trendType}トレンド（傾き: ${slope.toFixed(2)}/期間）。全体の成長率: ${totalGrowthRate.toFixed(1)}%`,
      confidence: 82,
      actionable: slope > 0 ? '現在の戦略継続で更なる成長期待' : '戦略見直しと改善施策が必要',
      priority,
      data: { slope, totalGrowthRate, intercept }
    });
    
    return insights;
  }

  /**
   * 顧客セグメンテーション（RFM分析）
   */
  analyzeCustomerSegments(customers: CustomerData[]): Insight[] {
    const insights: Insight[] = [];
    
    // 各指標の平均計算
    const avgRecency = customers.reduce((sum, c) => sum + c.recency, 0) / customers.length;
    const avgFrequency = customers.reduce((sum, c) => sum + c.frequency, 0) / customers.length;
    const avgMonetary = customers.reduce((sum, c) => sum + c.monetary, 0) / customers.length;
    
    // セグメント分類ロジック
    const segments = {
      champions: customers.filter(c => 
        c.recency < avgRecency && c.frequency > avgFrequency && c.monetary > avgMonetary),
      loyalCustomers: customers.filter(c => 
        c.recency < avgRecency * 1.5 && c.frequency > avgFrequency),
      potentialLoyalists: customers.filter(c => 
        c.recency < avgRecency && c.frequency <= avgFrequency),
      atRisk: customers.filter(c => 
        c.recency > avgRecency * 1.5 && c.frequency <= avgFrequency),
      cannotLoseThem: customers.filter(c => 
        c.recency > avgRecency && c.monetary > avgMonetary * 1.5),
      hibernating: customers.filter(c => 
        c.recency > avgRecency * 2 && c.frequency <= avgFrequency * 0.5)
    };
    
    // 各セグメントの洞察生成
    Object.entries(segments).forEach(([segmentKey, segmentCustomers]) => {
      if (segmentCustomers.length === 0) return;
      
      const segmentInfo = this.getSegmentInfo(segmentKey);
      const count = segmentCustomers.length;
      const percentage = (count / customers.length * 100);
      const avgF = segmentCustomers.reduce((sum, c) => sum + c.frequency, 0) / count;
      const avgM = segmentCustomers.reduce((sum, c) => sum + c.monetary, 0) / count;
      
      insights.push({
        type: '顧客セグメント洞察',
        insight: `${segmentInfo.name}: ${count}人（${percentage.toFixed(1)}%）- 平均購入頻度${avgF.toFixed(1)}回、平均購入額${avgM.toFixed(0)}円`,
        confidence: 78,
        actionable: segmentInfo.action,
        priority: this.getSegmentPriority(segmentKey, percentage),
        data: { segment: segmentKey, count, percentage, avgFreq: avgF, avgMon: avgM }
      });
    });
    
    return insights;
  }

  /**
   * 相関分析
   */
  analyzeCorrelations(data: DataPoint[]): Insight[] {
    const insights: Insight[] = [];
    
    // 数値列を抽出
    const numericColumns = this.getNumericColumns(data);
    if (numericColumns.length < 2) return insights;
    
    // ペアワイズ相関計算
    for (let i = 0; i < numericColumns.length; i++) {
      for (let j = i + 1; j < numericColumns.length; j++) {
        const col1 = numericColumns[i];
        const col2 = numericColumns[j];
        
        const values1 = data.map(d => Number(d[col1])).filter(v => !isNaN(v));
        const values2 = data.map(d => Number(d[col2])).filter(v => !isNaN(v));
        
        if (values1.length !== values2.length) continue;
        
        const correlation = this.calculateCorrelation(values1, values2);
        
        if (Math.abs(correlation) > 0.5) {
          const direction = correlation > 0 ? '正の' : '負の';
          const strength = Math.abs(correlation) > 0.8 ? '非常に強い' : 
                          Math.abs(correlation) > 0.6 ? '強い' : '中程度の';
          
          insights.push({
            type: '相関洞察',
            insight: `${col1}と${col2}に${strength}${direction}相関（r=${correlation.toFixed(3)}）`,
            confidence: Math.min(95, Math.abs(correlation) * 100),
            actionable: `${col1}の最適化により${col2}の${correlation > 0 ? '向上' : '調整'}が期待される`,
            priority: Math.abs(correlation) > 0.7 ? 'high' : 'medium',
            data: { var1: col1, var2: col2, correlation }
          });
        }
      }
    }
    
    return insights;
  }

  /**
   * 異常値検出
   */
  detectAnomalies(data: TimeSeriesData[], threshold: number = 2.5): Insight[] {
    const insights: Insight[] = [];
    const values = data.map(d => d.value);
    
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    
    const anomalies: Array<{index: number, value: number, date: Date, zScore: number}> = [];
    
    values.forEach((value, index) => {
      const zScore = Math.abs(value - mean) / stdDev;
      if (zScore > threshold) {
        anomalies.push({
          index,
          value,
          date: data[index].date,
          zScore
        });
      }
    });
    
    if (anomalies.length > 0) {
      const mostExtreme = anomalies.reduce((max, current) => 
        current.zScore > max.zScore ? current : max
      );
      
      insights.push({
        type: '異常値洞察',
        insight: `${anomalies.length}個の異常値を検出。最大偏差: ${mostExtreme.zScore.toFixed(1)}σ（${mostExtreme.date.toISOString().split('T')[0]}: ${mostExtreme.value.toFixed(0)}）`,
        confidence: 88,
        actionable: '異常値の原因分析が必要（キャンペーン効果、システム障害、外部要因等の調査）',
        priority: anomalies.length > data.length * 0.05 ? 'high' : 'medium',
        data: { anomalyCount: anomalies.length, maxDeviation: mostExtreme }
      });
    }
    
    return insights;
  }

  /**
   * 総合分析実行
   */
  performComprehensiveAnalysis(data: {
    timeSeries?: TimeSeriesData[];
    customers?: CustomerData[];
    correlationData?: DataPoint[];
  }): Insight[] {
    let allInsights: Insight[] = [];
    
    if (data.timeSeries) {
      allInsights.push(...this.analyzeSeasonality(data.timeSeries));
      allInsights.push(...this.analyzeTrend(data.timeSeries));
      allInsights.push(...this.detectAnomalies(data.timeSeries));
    }
    
    if (data.customers) {
      allInsights.push(...this.analyzeCustomerSegments(data.customers));
    }
    
    if (data.correlationData) {
      allInsights.push(...this.analyzeCorrelations(data.correlationData));
    }
    
    // 洞察を信頼度と優先度でソート
    allInsights.sort((a, b) => {
      const priorityWeight = { high: 3, medium: 2, low: 1 };
      const priorityDiff = priorityWeight[b.priority] - priorityWeight[a.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.confidence - a.confidence;
    });
    
    this.insights = allInsights;
    return allInsights;
  }

  /**
   * 洞察レポート生成
   */
  generateReport(): string {
    const report = [
      '='.repeat(60),
      '🎯 Serena洞察分析レポート',
      '=' .repeat(60),
      '',
      `📊 総洞察数: ${this.insights.length}件`,
      `🔥 高優先度: ${this.insights.filter(i => i.priority === 'high').length}件`,
      `⚡ 中優先度: ${this.insights.filter(i => i.priority === 'medium').length}件`,
      `💡 低優先度: ${this.insights.filter(i => i.priority === 'low').length}件`,
      '',
      '-'.repeat(50),
      '🏆 洞察一覧（優先度順）',
      '-'.repeat(50)
    ];
    
    this.insights.forEach((insight, index) => {
      const priorityIcon = insight.priority === 'high' ? '🚨' : 
                          insight.priority === 'medium' ? '⚡' : '💡';
      
      report.push(
        '',
        `【${index + 1}】${insight.type} ${priorityIcon}`,
        `📊 ${insight.insight}`,
        `🎯 信頼度: ${insight.confidence}%`,
        `💡 推奨: ${insight.actionable}`
      );
    });
    
    return report.join('\n');
  }

  // ヘルパーメソッド
  private getSegmentInfo(segmentKey: string) {
    const segmentMap: Record<string, {name: string, action: string}> = {
      champions: { name: 'チャンピオン顧客', action: '特別な体験と報酬プログラム' },
      loyalCustomers: { name: 'ロイヤル顧客', action: 'アップセル・クロスセル機会の提供' },
      potentialLoyalists: { name: 'ロイヤル候補', action: 'ロイヤルティプログラムへの誘導' },
      atRisk: { name: 'リスク顧客', action: 'リワードやパーソナライズ対応' },
      cannotLoseThem: { name: '失えない顧客', action: '個人的なアテンションと専用サポート' },
      hibernating: { name: '休眠顧客', action: '再活性化キャンペーンの実施' }
    };
    return segmentMap[segmentKey] || { name: 'その他', action: '個別戦略の検討' };
  }

  private getSegmentPriority(segmentKey: string, percentage: number): 'high' | 'medium' | 'low' {
    if (['champions', 'atRisk', 'cannotLoseThem'].includes(segmentKey)) return 'high';
    if (percentage > 20) return 'medium';
    return 'low';
  }

  private getNumericColumns(data: DataPoint[]): string[] {
    if (data.length === 0) return [];
    return Object.keys(data[0]).filter(key => 
      data.every(row => typeof row[key] === 'number' && !isNaN(Number(row[key])))
    );
  }

  private calculateCorrelation(x: number[], y: number[]): number {
    const n = x.length;
    if (n === 0) return 0;
    
    const sumX = x.reduce((sum, val) => sum + val, 0);
    const sumY = y.reduce((sum, val) => sum + val, 0);
    const sumXY = x.reduce((sum, val, i) => sum + val * y[i], 0);
    const sumX2 = x.reduce((sum, val) => sum + val * val, 0);
    const sumY2 = y.reduce((sum, val) => sum + val * val, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    return denominator === 0 ? 0 : numerator / denominator;
  }
}

export { SerenaInsightEngine, Insight, TimeSeriesData, CustomerData, DataPoint };
