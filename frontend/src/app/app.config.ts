import {
    ApplicationConfig, DEFAULT_CURRENCY_CODE,
    LOCALE_ID,
    provideBrowserGlobalErrorListeners,
    provideZoneChangeDetection
} from '@angular/core';
import { provideRouter } from '@angular/router';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptors} from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import { MessageService } from 'primeng/api';
import { registerLocaleData } from '@angular/common';
import localePt from '@angular/common/locales/pt';
import localePtExtra from '@angular/common/locales/extra/pt';
import Aura from '@primeuix/themes/aura';

import { routes } from './app.routes';
import { errorInterceptor } from './interceptors/error.interceptor';
import {provideEnvironmentNgxMask} from "ngx-mask";
import {idempotencyInterceptor} from "./interceptors/idempotency.interceptor";

registerLocaleData(localePt, 'pt-BR', localePtExtra);

export const appConfig: ApplicationConfig = {
    providers: [
        provideHttpClient(withInterceptors([errorInterceptor, idempotencyInterceptor])),
        provideBrowserGlobalErrorListeners(),
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideRouter(routes),
        provideEnvironmentNgxMask(),
        provideAnimationsAsync(),
        providePrimeNG({
            theme: {
                preset: Aura,
                options: {
                    darkModeSelector: false
                },
            }
        }),
        MessageService,
        { provide: LOCALE_ID, useValue: 'pt-BR' },
        { provide: DEFAULT_CURRENCY_CODE, useValue: 'BRL' }
    ]
};
