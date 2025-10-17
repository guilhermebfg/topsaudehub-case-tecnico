import { Routes } from '@angular/router';
import {Products} from './core/products/products';
import {Index} from './core/index';
import {Customers} from './core/customers/customers';
import {Orders} from './core/orders/orders';

export const routes: Routes = [
    {
        path: '',
        component: Index
    },
    {
        path: 'products',
        component: Products
    },
    {
        path: 'customers',
        component: Customers
    },
    {
        path: 'orders',
        component: Orders
    },
];
