import {HttpInterceptorFn} from '@angular/common/http';
import {inject} from '@angular/core';
import {from} from 'rxjs';
import {switchMap} from 'rxjs/operators';
import {IdempotencyService} from '../services/idempotency.service'; // <- caminho correto

export const idempotencyInterceptor: HttpInterceptorFn = (req, next) => {
    const idem = inject(IdempotencyService);

    const needsIdem = req.method === 'POST' && /\/api\/orders(\/|$)/.test(req.url);

    if (!needsIdem || req.headers.has('Idempotency-Key')) {
        return next(req);
    }

    return from(idem.getKeyFor('create-order', req.body)).pipe(switchMap((key: string) => next(req.clone({
        setHeaders: {'Idempotency-Key': key}
    }))));
};