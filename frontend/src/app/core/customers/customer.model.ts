import {Product} from '../products/product.model';

export interface Customer {
  id: number;
  name: string;
  email: string;
  document: string;
  created_at?: string;
  updated_at?: string;
}

export interface CustomerFormData {
  id?: number | null;
  name: string;
  email: string;
  document: string;
}

export interface CustomerFilterParams {
  id?: number | null;
  name?: string | null;
  email?: string | null;
  document?: string | null;
  created_min?: string | null;
  first?: number;
  rows?: number;
}

export interface CustomerListResponse {
  items: Customer[];
  total: number;
}
