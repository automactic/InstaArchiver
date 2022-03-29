import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { NbWindowService, NbWindowControlButtonsConfig } from '@nebular/theme';

import { ProfileService, Profile } from '../services/profile.service';
import { ProfileEditComponent } from '../profile-edit/profile-edit.component';

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  profileService: ProfileService

  profile$: Observable<Profile>
  username?: string
  year?: string
  month?: string
  selectedShortcode?: string

  constructor(
    private route: ActivatedRoute,
    private router: Router, 
    private windowService: NbWindowService,
    profileService: ProfileService
  ) {
    this.profileService = profileService
    this.profile$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        return this.profileService.get(queryParams.get('username') ?? '')
      })
    )
    this.route.queryParamMap.subscribe(queryParams => {
      this.username = queryParams.get('username') ?? undefined
      this.year = queryParams.get('year') ?? undefined
      this.month = queryParams.get('month') ?? undefined
      this.selectedShortcode = queryParams.get('selected') ?? undefined
    })
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

  openEditWindow(username: string, display_name: string) {
    const config: NbWindowControlButtonsConfig = {
      minimize: false,
      maximize: false,
      fullScreen: false,
      close: true,
    }
    const context = { username: username, display_name: display_name }
    this.windowService.open(
      ProfileEditComponent, 
      { title: `Edit Profile: ${username}`, buttons: config, context: context }
    )
  }

  openInstagramProfile(username: string) {
    window.open(`https://www.instagram.com/${username}/`, '_blank')
  }
}
