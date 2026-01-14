import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

/**
 * DataStack: DynamoDB tables for stock data and debate cache
 * - companies: Stock company metadata (ticker, name, sector, etc)
 * - financial_reports: Financial metrics and statements
 * - ohlc_prices: OHLC candlestick data by date
 * - debate_results: Cached debate outcomes for query acceleration
 */
export class DataStack extends cdk.Stack {
  readonly companiesTable: dynamodb.Table;
  readonly financialReportsTable: dynamodb.Table;
  readonly ohlcPricesTable: dynamodb.Table;
  readonly debateResultsTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Companies table: ticker -> company metadata
    this.companiesTable = new dynamodb.Table(this, 'CompaniesTable', {
      partitionKey: { name: 'ticker', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // Ideal for variable stock data access
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true
      }
    });
    cdk.Tags.of(this.companiesTable).add('Component', 'DataStore');
    cdk.Tags.of(this.companiesTable).add('Purpose', 'CompanyMetadata');

    // Financial Reports table: ticker + timestamp -> financial metrics
    this.financialReportsTable = new dynamodb.Table(this, 'FinancialReportsTable', {
      partitionKey: { name: 'ticker', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true
      }
    });
    cdk.Tags.of(this.financialReportsTable).add('Component', 'DataStore');
    cdk.Tags.of(this.financialReportsTable).add('Purpose', 'FinancialMetrics');

    // OHLC Prices table: ticker + date -> price data
    this.ohlcPricesTable = new dynamodb.Table(this, 'OhlcPricesTable', {
      partitionKey: { name: 'ticker', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'date', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true
      },
      timeToLiveAttribute: 'ttl' // Auto-expire old cached price data
    });
    cdk.Tags.of(this.ohlcPricesTable).add('Component', 'DataStore');
    cdk.Tags.of(this.ohlcPricesTable).add('Purpose', 'PriceData');

    // Debate Results cache: ticker + timeframe + timestamp -> debate outcome
    this.debateResultsTable = new dynamodb.Table(this, 'DebateResultsTable', {
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING }, // ticker#timeframe
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING }, // timestamp
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      timeToLiveAttribute: 'ttl' // Cache debates for 7 days
    });
    cdk.Tags.of(this.debateResultsTable).add('Component', 'DataStore');
    cdk.Tags.of(this.debateResultsTable).add('Purpose', 'DebateCache');

    // GSI for debate results: query by creation timestamp (recent debates)
    this.debateResultsTable.addGlobalSecondaryIndex({
      indexName: 'CreatedAtIndex',
      partitionKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL
    });

    // Output table names for Lambda functions
    new cdk.CfnOutput(this, 'CompaniesTableName', {
      value: this.companiesTable.tableName,
      exportName: 'CompaniesTableName'
    });

    new cdk.CfnOutput(this, 'FinancialReportsTableName', {
      value: this.financialReportsTable.tableName,
      exportName: 'FinancialReportsTableName'
    });

    new cdk.CfnOutput(this, 'OhlcPricesTableName', {
      value: this.ohlcPricesTable.tableName,
      exportName: 'OhlcPricesTableName'
    });

    new cdk.CfnOutput(this, 'DebateResultsTableName', {
      value: this.debateResultsTable.tableName,
      exportName: 'DebateResultsTableName'
    });
  }
}
