import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
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
    private router: Router, 
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
    this.route.queryParamMap.subscribe(queryParams => {
      this.username = queryParams.get('username') ?? undefined
      this.year = queryParams.get('year') ?? undefined
      this.month = queryParams.get('month') ?? undefined
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
}
