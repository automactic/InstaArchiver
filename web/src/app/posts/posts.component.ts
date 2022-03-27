import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { NbWindowService, NbWindowControlButtonsConfig } from '@nebular/theme';

import { ProfileService, Profile, ProfileConfiguration } from '../services/profile.service';
import { ProfileEditComponent } from '../profile-edit/profile-edit.component'

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  profileService: ProfileService;
  username?: string;
  profile$: Observable<Profile>;

  constructor(
    private route: ActivatedRoute, 
    private windowService: NbWindowService, 
    profileService: ProfileService
  ) {
    this.profileService = profileService;
    this.route.paramMap.subscribe(param => {
      this.username = param.get("username") ?? undefined;
    })
    this.profile$ = this.route.paramMap.pipe(
      switchMap(params => {
        return this.profileService.get(params.get("username") ?? "")
      })
    );
  }

  openEditWindow(username: string, display_name: string) {
    const config: NbWindowControlButtonsConfig = {
      minimize: false,
      maximize: false,
      fullScreen: false,
      close: true,
    };
    const context = { username: username, display_name: display_name }
    this.windowService.open(
      ProfileEditComponent, 
      { title: `Edit Profile: ${username}`, buttons: config, context: context }
    );
  }

  openInstagramProfile(username: string) {
    window.open(`https://www.instagram.com/${username}/`, '_blank');
  }
}
