import { Product } from '../products/product.model';
import { Customer } from '../customers/customer.model';

export enum OrderStatus {
  CREATED = 'CREATED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED'
}

export interface OrderItem {
  id?: number;
  product_id: number;
  product?: Product;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface Order {
  id: number;
  customer_id: number;
  customer?: Customer;
  total_amount: number;
  status: OrderStatus;
  items: OrderItem[];
  created_at?: string;
  updated_at?: string;
}

export interface OrderFormData {
  id?: number | null;
  customer_id: number;
  items: OrderItemFormData[];
}

export interface OrderItemFormData {
  id?: number | null;
  product_id?: number;
  quantity: number;
  unit_price?: number;
}

export interface OrderFilterParams {
  id?: number;
  customer?: string;
  total_amount?: number;
  status?: OrderStatus;
  created_min?: string;
  first?: number;
  rows?: number;
  sort_field?: string;
  sort_order?: number;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
}

export interface OrderStatusOption {
  id: OrderStatus | null;
  label: string;
  severity: "danger" | "success" | "info" | "warn" | "secondary" | "contrast" | null | undefined ;
}
