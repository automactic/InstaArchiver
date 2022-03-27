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
    this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        this.username = queryParams.get('username') ?? undefined;
        this.year = queryParams.get('year') ?? undefined;
        this.month = queryParams.get('month') ?? undefined;
        return this.postService.list(0, 5, this.username, this.year, this.month);
      })
    ).subscribe(response => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      // this.loading = false;
      // this.posts = response.posts;
    })
    this.profile$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        return this.profileService.get(queryParams.get('username') ?? '')
      })
    )
  }
}
