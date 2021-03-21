import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { switchMap } from 'rxjs/operators';
import { NbMenuItem } from '@nebular/theme';

import { Post, PostItem, PostService } from '../services/post.service';
import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  postService: PostService;
  profileService: ProfileService;

  username?: string;
  year?: string;
  month?: string;
  loading = true;
  posts: Post[] = [];

  items: NbMenuItem[] = [
    {
      title: 'Profile',
      expanded: true,
      badge: {
        text: '30',
        status: 'primary',
      },
      children: [
        {
          title: 'Messages',
          badge: {
            text: '99+',
            status: 'danger',
          },
        },
        {
          title: 'Notifications',
          badge: {
            dotMode: true,
            status: 'warning',
          },
        },
        {
          title: 'Emails',
          badge: {
            text: 'new',
            status: 'success',
          },
        },
      ],
    },
  ];
  
  constructor(
    private route: ActivatedRoute, 
    private router: Router, 
    postService: PostService, 
    profileService: ProfileService
  ) {
    this.postService = postService;
    this.profileService = profileService;
    this.route.queryParamMap.pipe(
      switchMap(queryParam => {
        this.username = queryParam.get("username") ?? undefined;
        this.year = queryParam.get("year") ?? undefined;
        this.month = queryParam.get("month") ?? undefined;
        return this.postService.list(0, 5, this.username, this.year, this.month);
      })
    ).subscribe(response => {
      window.scrollTo({ top: 0, behavior: 'smooth'});
      this.loading = false;
      this.posts = response.posts;
    })
  }

  clearSelectedProfile() {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { username: null}, 
      queryParamsHandling: 'merge' 
    });
  }

  selectedProfileChanged(username: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { username: username}, 
      queryParamsHandling: 'merge' 
    });
  }

  selectedYearChanged(year: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { year: year}, 
      queryParamsHandling: 'merge' 
    });
  }

  selectedMonthChanged(month: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { month: month}, 
      queryParamsHandling: 'merge' 
    });
  }

  loadNext() {
    if (this.loading) { return }
    this.loading = true;
    this.postService.list(this.posts.length, 5, this.username, this.year, this.month).subscribe( response_data => {
      this.posts.push(...response_data.posts);
      this.loading = false;
    })
  }

  delete(post: Post, item: PostItem, postIndex: number, itemIndex: number) {
    this.postService.delete(post.shortcode, item.index).subscribe( _ => {
      if (post.items.length == 1) {
        this.posts.splice(postIndex, 1);
      } else {
        post.items.splice(itemIndex, 1);
      }
    })
  }
}
