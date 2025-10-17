export interface Product {
  id: number;
  name: string;
  sku: string;
  price: number;
  stock_qty: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ProductFormData {
  id?: number | null;
  name: string;
  sku: string;
  price: number;
  stock_qty: number;
  is_active: boolean;
}

export interface ProductFilterParams {
  id?: number | null;
  name?: string | null;
  sku?: string | null;
  price?: number | null;
  stock_qty?: number | null;
  is_active?: boolean | null;
  created_min?: string | null;
  first?: number;
  rows?: number;
  sort_field?: string;
  sort_order?: number;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
}
