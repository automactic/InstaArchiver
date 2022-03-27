import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { ProfileService, Profile } from '../services/profile.service';
import { PostService, Post } from '../services/post.service';

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  postService: PostService;
  profileService: ProfileService

  profile$: Observable<Profile>
  username?: string;
  year?: string;
  month?: string;

  constructor(
    private route: ActivatedRoute,
    postService: PostService,
    profileService: ProfileService
  ) {
    this.postService = postService
    this.profileService = profileService
    this.profile$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        return this.profileService.get(queryParams.get('username') ?? '')
      })
    )
  }
}
