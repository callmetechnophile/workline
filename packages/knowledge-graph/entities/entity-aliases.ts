/**
 * Entity Alias schemas and categories.
 */

export enum AliasType {
  ABBREVIATION = "ABBREVIATION",
  TRADE_NAME = "TRADE_NAME",
  PART_VARIANT = "PART_VARIANT",
  COMMON_NAME = "COMMON_NAME",
  MODEL_ALIAS = "MODEL_ALIAS",
  USER_DEFINED = "USER_DEFINED",
  SOURCE_DEFINED = "SOURCE_DEFINED",
}

export interface EntityAlias {
  aliasId: string;
  entityId: string;
  alias: string;
  aliasType: AliasType;
  source: string;
  confidence: number;
}
