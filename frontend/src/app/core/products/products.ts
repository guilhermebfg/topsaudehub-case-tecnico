import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {CurrencyPipe, DatePipe} from '@angular/common';
import {firstValueFrom, Subject, takeUntil} from 'rxjs';
import {TableLazyLoadEvent, TableModule} from 'primeng/table';
import {Dialog} from 'primeng/dialog';
import {InputNumber} from 'primeng/inputnumber';

import {ProductService} from './product.service';
import {LoadingService} from '../loading/loading.service';
import {NotificationService} from '../../services/notification.service';
import {ProductFilterParams, ProductListResponse} from './product.model';
import {DatePicker} from "primeng/datepicker";
import {Select} from "primeng/select";
import {NgxMaskDirective} from "ngx-mask";

@Component({
    selector: 'app-products',
    imports: [TableModule, CurrencyPipe, DatePipe, Dialog, ReactiveFormsModule, InputNumber, DatePicker, Select, NgxMaskDirective],
    templateUrl: './products.html',
    styleUrl: './products.scss'
})
export class Products implements OnDestroy {
    public products: ProductListResponse = {items: [], total: 0};
    public productForm: FormGroup;
    public productsFilter: FormGroup;
    public modalProductFormVisible: boolean = false;
    public today: Date = new Date();

    public status = [
        {id: null, label: 'Todos'},
        {id: true, label: 'Ativo'},
        {id: false, label: 'Inativo'}
    ];

    public paginator: ProductFilterParams = {
        first: 0, rows: 5, sort_field: 'id', sort_order: -1
    };

    private destroy$ = new Subject<void>();

    constructor(private productService: ProductService, private fb: FormBuilder, private loading: LoadingService, private notification: NotificationService) {
        this.productForm = this.createProductForm();
        this.productsFilter = this.createFilterForm();

        this.productsFilter.valueChanges
            .pipe(takeUntil(this.destroy$))
            .subscribe(() => {
                this.loadProducts();
            });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    private createProductForm(): FormGroup {
        let form = this.fb.group({
            id: [null],
            name: [null, Validators.required],
            sku: [null, Validators.required],
            price: [null, Validators.compose([Validators.required, Validators.min(1)])],
            stock_qty: [1, Validators.required],
            is_active: [true, Validators.required]
        });

        form.get('sku')?.valueChanges.subscribe((value: string | null) => {
            if (value) {
                this.productForm.get('sku')?.setValue(value.toUpperCase(), { emitEvent: false });
            }
        })

        return form
    }

    private createFilterForm(): FormGroup {
        return this.fb.group({
            id: [null],
            name: [null],
            sku: [null],
            price: [null],
            stock_qty: [null],
            is_active: [null],
            created_min: [null]
        });
    }

    public loadProducts(event: TableLazyLoadEvent | null = null): void {
        if (event != null) {
            this.paginator = {
                first: event.first ?? this.paginator.first,
                rows: event.rows ?? this.paginator.rows,
                sort_order: event.sortOrder ?? this.paginator.sort_order,
                sort_field: event.sortField != null ? typeof event.sortField !== 'string' ? event.sortField[0] : event.sortField : this.paginator.sort_field
            };
        }

        const filter = this.productsFilter.getRawValue();

        const params: ProductFilterParams = {
            id: filter.id,
            name: filter.name ?? '',
            sku: filter.sku ?? '',
            price: filter.price ?? '',
            stock_qty: filter.stock_qty ?? '',
            is_active: filter.is_active ?? '',
            created_min: filter.created_min ? new Date(filter.created_min).toISOString() : '',
            ...this.paginator
        };

        // Remove empty values
        Object.keys(params).forEach((key) => {
            const value = params[key as keyof ProductFilterParams];
            if (value === '' || value === null || value === undefined) {
                delete params[key as keyof ProductFilterParams];
            }
        });

        this.productService.getProducts(params)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: (res) => {
                    this.products = res.data;
                }, error: (error) => {
                    console.error('Error loading products:', error);
                }
            });
    }

    public get productId(): number | null {
        return this.productForm.get('id')?.value;
    }

    public async openModalFormProduct(productId: number | null = null): Promise<void> {
        if (productId != null) {
            let product = await firstValueFrom(this.productService.getProduct(productId))
            if (product) {
                this.productForm.patchValue(product.data);
            }
        } else {
            this.productForm = this.createProductForm();
        }

        this.modalProductFormVisible = true;
    }

    public async saveProduct(): Promise<void> {
        if (!this.productForm.valid) {
            this.notification.warning('Por favor, preencha todos os campos obrigatórios');
            return;
        }

        this.loading.spinnerOn();

        const payload = this.productForm.getRawValue();

        try {
            if (payload.id != null) {
                await this.productService.updateProduct(payload).toPromise();
                this.notification.success('Produto atualizado com sucesso');
            } else {
                await this.productService.createProduct(payload).toPromise();
                this.notification.success('Produto criado com sucesso');
            }

            this.loadProducts();
            this.modalProductFormVisible = false;
        } catch (error) {
            console.error('Error saving product:', error);
        } finally {
            this.loading.spinnerOff();
        }
    }
}
