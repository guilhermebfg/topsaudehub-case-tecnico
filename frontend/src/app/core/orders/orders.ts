import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import {CurrencyPipe, DatePipe, NgClass} from '@angular/common';
import {firstValueFrom, Subject, takeUntil} from 'rxjs';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { Dialog } from 'primeng/dialog';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { Accordion, AccordionContent, AccordionHeader, AccordionPanel } from 'primeng/accordion';

import { OrderService } from './order.service';
import { CustomerService } from '../customers/customer.service';
import { ProductService } from '../products/product.service';
import { LoadingService } from '../loading/loading.service';
import { NotificationService } from '../../services/notification.service';
import {
    Order,
    OrderStatus,
    OrderStatusOption,
    OrderFilterParams,
    OrderListResponse,
    OrderItem
} from './order.model';
import {Customer, CustomerFilterParams} from '../customers/customer.model';
import { Product } from '../products/product.model';
import {InputNumber} from 'primeng/inputnumber';
import {Select} from "primeng/select";
import {DatePicker} from "primeng/datepicker";
import {debounceTime} from "rxjs/operators";
import {Badge} from "primeng/badge";

interface OrderItemFormGroup {
    id: FormControl<number | null>;
    unit_price: FormControl<number | null>;
    product: FormControl<Product | string | null>;
    quantity: FormControl<number | null>;
    line_total: FormControl<number | null>;
}

@Component({
    selector: 'app-orders',
    imports: [
        DatePipe,
        Dialog,
        FormsModule,
        ReactiveFormsModule,
        TableModule,
        CurrencyPipe,
        AutoComplete,
        Accordion,
        AccordionPanel,
        AccordionHeader,
        AccordionContent,
        InputNumber,
        Select,
        DatePicker,
        Badge
    ],
    templateUrl: './orders.html',
    styleUrl: './orders.scss'
})
export class Orders implements OnInit, OnDestroy {
    public orders: OrderListResponse = { items: [], total: 0 };
    public order: Order | null = null;
    public orderForm: FormGroup;
    public modalOrderFormVisible: boolean = false;
    public customerSuggestions: Customer[] = [];
    public productSuggestions: Product[] = [];
    public activeAccordion: number = 0;
    public orderFilter: FormGroup;
    public today: Date = new Date();

    public orderStatus: OrderStatusOption[] = [
        { id: null, label: 'Todos', severity: 'info' },
        { id: OrderStatus.CREATED, label: 'Criado', severity: 'warn' },
        { id: OrderStatus.PAID, label: 'Pago', severity: 'success' },
        { id: OrderStatus.CANCELLED, label: 'Cancelado', severity: 'danger' }
    ];

    public paginator: OrderFilterParams = {
        first: 0,
        rows: 5,
        sort_field: 'id',
        sort_order: -1
    };

    private destroy$ = new Subject<void>();

    constructor(
        private orderService: OrderService,
        private customerService: CustomerService,
        private productService: ProductService,
        private fb: FormBuilder,
        private loading: LoadingService,
        private notification: NotificationService
    ) {
        this.orderForm = this.createOrderForm();
        this.orderFilter = this.createFilterForm();

        this.orderFilter
            .valueChanges
            .pipe(takeUntil(this.destroy$))
            .pipe(debounceTime(500))
            .subscribe(() => {
                this.loadOrders();
            })
    }

    ngOnInit(): void {
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    private createOrderForm(): FormGroup {
        return this.fb.group({
            id: [null],
            customer: [null, Validators.required],
            total_amount: [0, Validators.required],
            status: [null, Validators.required],
            items: this.fb.array([])
        });
    }

    private createFilterForm(): FormGroup {
        return this.fb.group({
            id: [null],
            customer: [null],
            total_amount: [null],
            status: [null],
            created_min: [null]
        });
    }

    public get itemsFormArray(): FormArray {
        return this.orderForm.get('items') as FormArray;
    }

    public get itemsFormGroups(): FormGroup[] {
        return this.itemsFormArray.controls as FormGroup[];
    }

    private createItemFormGroup(): FormGroup<OrderItemFormGroup> {
        const item = this.fb.group<OrderItemFormGroup>({
            id: new FormControl(null),
            unit_price: new FormControl(0),
            product: new FormControl<Product | string | null>(null, Validators.required),
            quantity: new FormControl(1),
            line_total: new FormControl(0)
        });

        // Calculate line total when quantity or price changes
        item.valueChanges
            .pipe(takeUntil(this.destroy$))
            .subscribe(() => {
                this.calculateAmounts()
            });

        return item;
    }

    private calculateAmounts(): void {
        let totalAmount = 0;

        this.itemsFormGroups.forEach((item) => {
            let itemValue = item.value
            if (itemValue.unit_price != null && itemValue.quantity != null) {
                let totalAmountItem = itemValue.unit_price * itemValue.quantity;
                item.get('line_total')?.setValue(totalAmountItem, { emitEvent: false });
                totalAmount += totalAmountItem;
            }
        });

        this.orderForm.get('total_amount')?.setValue(totalAmount, { emitEvent: false });
    }

    public addItem(): void {
        const newItem = this.createItemFormGroup();
        newItem.get('product')?.valueChanges
            .pipe(takeUntil(this.destroy$))
            .subscribe((product: Product | string | null) => {
                if (product && typeof product !== 'string') {
                    newItem.patchValue({
                        unit_price: product.price,
                        line_total: product.price
                    });
                }
            })
        this.itemsFormArray.push(newItem);
    }

    public removeItem(index: number): void {
        this.itemsFormArray.removeAt(index);
        this.calculateAmounts()
    }

    public async customerSearch(event: AutoCompleteCompleteEvent): Promise<void> {
        const params = { name: event.query };

        this.customerService.getCustomers(params)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: (res) => {
                    this.customerSuggestions = res.data.items;
                },
                error: (error) => {
                    console.error('Error searching customers:', error);
                }
            });
    }

    public searchProducts(event: AutoCompleteCompleteEvent): void {
        const params = { name: event.query };

        this.productService.getProducts(params)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: (res) => {
                    this.productSuggestions = res.data.items;
                },
                error: (error) => {
                    console.error('Error searching customers:', error);
                }
            });
    }

    public getOrderStatusLabel(statusId: string): string {
        return this.orderStatus.find((status) => status.id === statusId)?.label ?? statusId;
    }

    public getOrderStatusSeverity(statusId: string) {
        return this.orderStatus.find((status) => status.id === statusId)?.severity ?? 'info';
    }

    public loadOrders(event: TableLazyLoadEvent | null = null): void {
        if (event != null) {
            this.paginator = {
                first: event.first ?? this.paginator.first,
                rows: event.rows ?? this.paginator.rows,
                sort_order: event.sortOrder ?? this.paginator.sort_order,
                sort_field: event.sortField != null
                    ? typeof event.sortField !== 'string'
                        ? event.sortField[0]
                        : event.sortField
                    : this.paginator.sort_field
            };
        }

        const filter = this.orderFilter.getRawValue();

        const payload: OrderFilterParams = {
            id: filter.name ?? '',
            customer: filter.customer ? encodeURIComponent(filter.customer) : '',
            total_amount: filter.total_amount ?? '',
            status: filter.status ?? '',
            created_min: filter.created_min ? new Date(filter.created_min).toISOString() : '',
            ...this.paginator
        };

        this.orderService.getOrders(payload)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: (res) => {
                    this.orders = res.data;
                },
                error: (error) => {
                    console.error('Error loading orders:', error);
                }
            });
    }

    public get orderId(): number | null {
        return this.orderForm.get('id')?.value;
    }

    public getItemMaxQuantity(i: number): number {
        let formGroup = this.itemsFormGroups.at(i)

        let quantity = 0

        let itemId = formGroup?.get('id')?.value

        if (itemId) {
            quantity += this.order?.items.find((item) => item.id == itemId)?.quantity ?? 0
        }

        quantity += formGroup?.get('product')?.value?.stock_qty ?? 0

        return quantity;
    }

    public openModalFormOrder(orderId: number | null = null): void {
        // Clear items array
        while (this.itemsFormArray.length) {
            this.itemsFormArray.removeAt(0);
        }

        if (orderId != null) {
            this.order = this.orders.items.find((o) => o.id === orderId) ?? null;

            if (this.order) {
                this.customerSuggestions = this.order.customer ? [this.order.customer] : [];

                this.orderForm.patchValue({
                    id: this.order.id,
                    customer: this.order.customer,
                    total_amount: this.order.total_amount,
                    status: this.order.status
                });

                // Add order items
                this.order.items.forEach((item) => {
                    const newItem = this.createItemFormGroup();
                    newItem.patchValue({
                        id: item.id,
                        unit_price: item.unit_price,
                        product: item.product,
                        quantity: item.quantity,
                        line_total: item.line_total
                    });

                    newItem.get('quantity')?.addValidators(Validators.max((item?.quantity ?? 0) + (item.product?.stock_qty ?? 0)));

                    this.itemsFormArray.push(newItem);
                });

                if (this.order.status !== OrderStatus.CREATED) {
                    this.orderForm.disable();
                } else {
                    this.orderForm.enable();
                }
            }
        } else {
            this.orderForm.enable();
            this.orderForm.reset({
                total_amount: 0,
                status: OrderStatus.CREATED
            });

            this.addItem()
        }

        this.activeAccordion = 0
        this.modalOrderFormVisible = true;
    }

    public async chargeOrder(): Promise<void> {
        if (this.order != null && this.order.status == OrderStatus.CREATED) {
            this.loading.spinnerOn();
            try {
                await firstValueFrom(this.orderService.chargeOrder(this.order?.id))
                this.notification.success('Pedido cobrado com sucesso');
                this.loading.spinnerOff();
                this.loadOrders();
                this.modalOrderFormVisible = false;
            } catch (error) {
                console.error('Error charging order:', error);
            }
        }
    }

    public async cancelOrder(): Promise<void> {
        if (this.order != null && this.order.status == OrderStatus.CREATED) {
            this.loading.spinnerOn();
            try {
                await firstValueFrom(this.orderService.cancelOrder(this.order?.id))
                this.notification.success('Pedido cancelado com sucesso');
                this.loading.spinnerOff();
                this.loadOrders();
                this.modalOrderFormVisible = false;
            } catch (error) {
                console.error('Error charging order:', error);
            }
        }
    }

    public async saveOrder(): Promise<void> {
        if (!this.orderForm.valid) {
            this.notification.warning('Por favor, preencha todos os campos obrigatórios');
            return;
        }

        this.loading.spinnerOn();

        const form = this.orderForm.getRawValue();

        let payload = {
            id: form.id,
            customer_id: form.customer.id,
            items: this.itemsFormGroups.map((item) => {
                const itemValue = item.getRawValue();
                return {
                    id: itemValue.id,
                    unit_price: itemValue.unit_price,
                    product_id: itemValue.product.id,
                    quantity: itemValue.quantity
                }
            })
        }

        try {
            if (payload.id != null) {
                await firstValueFrom(this.orderService.updateOrder(payload));
                this.notification.success('Pedido atualizado com sucesso');
            } else {
                await firstValueFrom(this.orderService.createOrder(payload));
                this.notification.success('Pedido criado com sucesso');
            }

            this.loadOrders();
            this.modalOrderFormVisible = false;
        } catch (error) {
            console.error('Error saving order:', error);
        } finally {
            this.loading.spinnerOff();
        }
    }

    public trackByOrderId(index: number, order: Order): number {
        return order.id;
    }

    public trackByItemId(index: number, item: OrderItem): number | undefined {
        return item.id ?? index;
    }
}
