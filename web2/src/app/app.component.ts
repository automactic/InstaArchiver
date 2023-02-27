import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { NbSidebarService, NbSidebarState, NbThemeService } from '@nebular/theme';

import { ProfileService, ListProfilesResponse } from './services/profile.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'InstaArchiver'
  sidebarState: NbSidebarState = 'expanded'
  year?: string
  month?: string

  response$?: Observable<ListProfilesResponse>
  profileService: ProfileService

  constructor(
    private sidebarService: NbSidebarService, 
    private themeService: NbThemeService, 
    private route: ActivatedRoute,
    private router: Router, 
    profileService: ProfileService
  ) {
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('default')
    })
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('dark')
    })
    this.route.queryParamMap.subscribe(queryParams => {
      this.year = queryParams.get('year') ?? undefined
      this.month = queryParams.get('month') ?? undefined
    })
    this.response$ = profileService.list()
    this.profileService = profileService
  }

  toggle() {
    this.sidebarService.toggle(true, 'left')
  }

  selectedYearChanged(year: string) {
    var queryParams: Record<string, string | null> = { year: year };
    if (year == null) {
      queryParams['month'] = null;
    }
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: queryParams, 
      queryParamsHandling: 'merge' 
    });
  }

  selectedMonthChanged(month: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { month: month }, 
      queryParamsHandling: 'merge' 
    });
  }
}
