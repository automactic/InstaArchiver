import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { ProfileService, Profile } from '../services/profile.service';

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  profileService: ProfileService
  username?: string
  profile$: Observable<Profile>

  constructor(
    private route: ActivatedRoute,  
    profileService: ProfileService
  ) {
    this.profileService = profileService
    this.route.paramMap.subscribe(param => {
      this.username = param.get('username') ?? undefined;
    })
    this.profile$ = this.route.paramMap.pipe(
      switchMap(params => {
        return this.profileService.get(params.get('username') ?? '')
      })
    )
  }
}
