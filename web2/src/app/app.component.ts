import { Component } from '@angular/core';
import { Observable } from 'rxjs';

import { NbSidebarService, NbSidebarState, NbThemeService } from '@nebular/theme';

import { ProfileService, ListProfilesResponse } from './services/profile.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'InstaArchiver'
  response$?: Observable<ListProfilesResponse>
  profileService: ProfileService
  sidebarState: NbSidebarState = 'expanded'

  constructor(
    private sidebarService: NbSidebarService, 
    private themeService: NbThemeService, 
    profileService: ProfileService
  ) {
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('default')
    })
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('dark')
    })
    this.response$ = profileService.list()
    this.profileService = profileService
  }

  toggle() {
    this.sidebarService.toggle(true, 'left')
  }
}
