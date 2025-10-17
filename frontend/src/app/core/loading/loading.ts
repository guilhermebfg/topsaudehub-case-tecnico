import { Component, OnDestroy, OnInit } from '@angular/core';
import { ProgressSpinner } from 'primeng/progressspinner';
import { AsyncPipe } from '@angular/common';
import { LoadingService } from './loading.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-loading',
  imports: [ProgressSpinner, AsyncPipe],
  templateUrl: './loading.html',
  styleUrl: './loading.scss'
})
export class Loading {
  public loading$: Observable<boolean>;

  constructor(private loadingService: LoadingService) {
    this.loading$ = this.loadingService.loading$;
  }
}
